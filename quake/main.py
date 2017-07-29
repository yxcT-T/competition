import obspy
import os
import matplotlib.pyplot as plt


WORK_DIR = '/Users/yxc/Desktop/earthquake/example'
STA_N = 30
LTA_N = 100

THRESHOLD = 2
S_INTERVAL = 10
L_INTERVAL = 1000
MIN_BATCH_SIZE = 1
channel = {'BHE' : 'S', 'BHN' : 'S', 'BHZ' : 'P'}


def get_files():
    all_files = []
    for dirpath, dirnames, filenames in os.walk(WORK_DIR):
        for file in filenames:
            all_files.append(dirpath + '/' + file)
    all_files.sort()
    return all_files



def find(file):
    quakes = []
    st = obspy.read(file)
    tr = st[0]
    starttime = obspy.UTCDateTime(tr.stats.starttime)
    endtime = obspy.UTCDateTime(tr.stats.endtime)
    sum_sta = 0.0
    sum_lta = 0.0
    for i in range(LTA_N - STA_N, LTA_N):
        sum_sta += abs(tr.data[i])
    for i in range(LTA_N):
        sum_lta += abs(tr.data[i])
    thresholds = []
    for i in range(LTA_N, tr.stats.npts):
        sum_sta += abs(tr.data[i])
        sum_sta -= abs(tr.data[i - STA_N])
        sum_lta += abs(tr.data[i])
        sum_lta -= abs(tr.data[i - LTA_N])
        if sum_lta > 0:
            p = (sum_sta / STA_N) / (sum_lta / LTA_N)
            if p > THRESHOLD:
                thresholds.append(i)
    sp = 0
    lp = -1
    for i in range(1, len(thresholds)):
        if lp == -1 and i - sp >= MIN_BATCH_SIZE:
            lp = i - 1
            quakes.append(thresholds[sp])
        if lp != -1:
            if thresholds[i] - thresholds[lp] < L_INTERVAL:
                lp = i
            else:
                lp = -1
                sp = i
            continue
        if thresholds[i] - thresholds[i - 1] > S_INTERVAL:
            sp = i
    #print quakes
    #print tr.stats
    print quakes
    return quakes


def draw(ax, file):
    quakes = find(file)
    tr = obspy.read(file)[0]
    labels = []
    for i in range(0, 5):
        labels.append(tr.stats.npts / 5 * i)
    labels.append(tr.stats.npts)
    ax.set_xticks(labels)
    ax.set_ylabel(tr.stats.channel)
    ax.plot(tr.data)
    for x in quakes:
        ax.annotate('', xy=(x, 0),
                    xytext=(x, max(tr.data)),
                    arrowprops=dict(facecolor='red'),
                    horizontalalignment='left', verticalalignment='top')


def plot_three(file_a, file_b, file_c):
    fig = plt.figure()
    ax1 = fig.add_subplot(3, 1, 1)
    ax2 = fig.add_subplot(3, 1, 2)
    ax3 = fig.add_subplot(3, 1, 3)
    draw(ax1, file_a)
    draw(ax2, file_b)
    draw(ax3, file_c)
    plt.show()


def main():
    all_files = get_files()
    for i in range(0, len(all_files), 3):
        plot_three(all_files[i], all_files[i + 1], all_files[i + 2])


if __name__ == '__main__':
    main()