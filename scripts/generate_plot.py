import threading
from datetime import datetime
import sys
import json
import os


import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks


import matplotlib.pyplot as plt
import mplcursors
import mpld3

MU = 'Memory-Used'


class PlotBar:

    def __init__(self, value, name, color="black", linestyle="--", linewidth=2):
        self.x = value
        self.label = name
        self.color = color
        self.linestyle = linestyle
        self.linewidth = linewidth

    def get_data(self):
        return vars(self)

class MemoryPlotStat:

    def __init__(self, name, data, label=None):
        self.name = name
        self.data = data
        self.label = label if label else name
        self.data_der1 = None
        self.data_der2 = None
        self.data_der3 = None


    def calculate_der1(self, time):
        data_der1 = np.gradient(self.data, time)
        self.data_der1 = gaussian_filter1d(data_der1, sigma=5)
        return self.data_der3

    def calculate_der2(self, time):
        if self.data_der1 is None:
            self.calculate_der1(time)

        data_der2 = np.gradient(self.data_der1, time)
        self.data_der2 = gaussian_filter1d(data_der2, sigma=14)
        return self.data_der2

    def calculate_der3(self, time):
        if self.data_der2 is None:
            self.calculate_der2(time)

        data_der3 = np.gradient(self.data_der2, time)
        self.data_der3 = gaussian_filter1d(data_der3, sigma=15)
        return self.data_der3

    def apply_func(self, func):
        self.data = func(self.data)

    def add_data(self, data):
        self.data = np.append(self.data, data)

    def __str__(self):
        sb = f"Name: {self.name}; size: {len(self.data)}"

        sb += "\n\t- ".join([str(d) for d in self.data])

        return sb


class MemoryPlotGenerator:

    def __init__(self, *data_sets):
        self.data_sets = data_sets
        self.title = "Memory Usage"
        self.x_label = "Time (Seconds)"
        self.y_label = "Memory Used (KB)"
        self.start_bar = None
        self.end_bar = None
        self.bars = []


    def add_start_end_bars(self, start_bar, end_bar):
        self.start_bar = start_bar
        self.end_bar = end_bar

    def add_filter(self, *f):
        for data in self.data_sets:
            data.add_filter(*f)

        return self

    def remove_filter(self, *f):
        for data in self.data_sets:
            data.remove_filter(*f)

    def clear_filter(self):
        for data in self.data_sets:
            data.filter = None

    def __generic_plot(self):
        fig, ax = plt.subplots(figsize=(16, 9))

        lines = []

        for data_set in self.data_sets:
            for stat in data_set.get_stats():
            # if self.filters is None or stat.name in self.filters:
                line, = ax.plot(data_set.time, stat.data, label=f"{data_set.name} ({stat.label})")
                lines.append(line)

        ax.set_title(self.title)
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        ax.legend()

        cursor = mplcursors.cursor(lines, hover=True, annotation_kwargs={'arrowprops': None})

        @cursor.connect("add")
        def on_click(sel):
            for l in lines:
                l.set_linewidth(1)
                l.set_alpha(0.7)
                l.set_markeredgewidth(1)

            selected_line = sel.artist
            selected_line.set_linewidth(3)
            selected_line.set_alpha(1.0)
            selected_line.set_markeredgewidth(3)

            ax.figure.canvas.draw()

        @cursor.connect("add")
        def on_hover(sel):
            x, y = sel.target
            sel.annotation.set_text(f'{sel.artist.get_label()}: {y:.2f}')

            bbox = sel.annotation.get_bbox_patch()
            if bbox is not None:
                bbox.set(fc="white", alpha=0.6)


        return fig, ax

    def align_memory_data_sets(self):
        m_set0 = self.data_sets[0]
        start_time_0, end_time_0 = m_set0.get_allocation_start_end_time()


        for m_setx in self.data_sets[1:]:
            start_time_x, end_time_x = m_setx.get_allocation_start_end_time()
            offset_required = start_time_x - start_time_0
            m_setx.time -= offset_required

        return self

    def compile_to_html(self, filename):
        fig, _ = self.__generic_plot()
        mpld3.save_html(fig, filename)
        print(f"Plot saved as {filename}")

    def __background_show(self):
        fig, ax = self.__generic_plot()

        for i, bar in enumerate(self.bars):
            ax.axvline(**bar.get_data())

        if self.start_bar:
            ax.axvline(**self.start_bar.get_data())
        if self.end_bar:
            ax.axvline(**self.end_bar.get_data())


        plt.draw()
        plt.pause(0.1)

    def show_plot(self):
        fig, ax = self.__generic_plot()

        for i, bar in enumerate(self.bars):
            ax.axvline(**bar.get_data())

        if self.start_bar and self.end_bar:
            ax.axvline(**self.start_bar.get_data())
            ax.axvline(**self.end_bar.get_data())

        plt.show()
        # self.__background_show()
        # plot_thread = threading.Thread(target=self.__background_show())
        # plot_thread.daemon = True
        # plot_thread.start()
        # return plot_thread

    def close_plot(self):
        plt.close()

    def save_plot(self, filename):
        fig, _ = self.__generic_plot()
        fig.savefig(filename)
        print(f"Plot saved as {filename}")

class MemoryDataSet:

    def __init__(self, name, time, stats, start_time, end_time):
        self.name = name
        self.time = time
        self.stats = stats
        self.start_time = start_time
        self.end_time = end_time
        self.filters = []

    def get_allocation_start_end_index(self):
        mu_der2 = self.stats[MU].calculate_der2(self.time)

        allocation_end = np.argmin(mu_der2)
        allocation_start = np.argmax(mu_der2[:allocation_end])

        return allocation_start, allocation_end

    def get_allocation_start_end_time(self):
        s, e = self.get_allocation_start_end_index()
        return self.time[s], self.time[e]

    def __getitem__(self, item):
        return self.stats.get(item)

    def add_filter(self, *values):
        self.filters += values
        return self

    def remove_filter(self, *values):
        for v in values:
            while v in self.filters:
                self.filters.remove(v)

    def get_stats(self):
        return [stat for stat in self.stats.values() if len(self.filters) == 0 or stat.name in self.filters]

    def stat_names(self):
        return self.stats.keys()

    def apply_func(self, func):
        for stat in self.stats.values():
            stat.apply_func(func)

    def cut_end_time(self, end_time):
        closest_index = np.argmin(np.abs(self.time - end_time))
        self.time = self.time[:closest_index]
        for stat in self.stats.values():
            stat.data = stat.data[:closest_index]

    def append_data_set(self, mds):
        if self.start_time < mds.start_time:
            offset = mds.start_time - self.end_time
            new_times = [self.time[-1] + t + offset.seconds for t in mds.time]
            self.time = np.append(self.time, new_times)
            for key in mds.stats.keys():
                self.stats[key].add_data(mds.stats[key].data)

            self.end_time = mds.end_time




def find_next_intersection(stat1, stat2, start_index, after=True):
    diff = stat1 - stat2

    sign_diff = np.sign(diff)

    sign_changes = np.where(np.diff(sign_diff) != 0)[0] + 1

    if after:
        next_intersection = sign_changes[sign_changes > start_index]
    else:
        next_intersection = sign_changes[sign_changes < start_index]


    if len(next_intersection) > 0:
        return next_intersection[0]
    else:
        return None

def find_n_maxima(sk_der3, sk_der1, N):
    peaks, _ = find_peaks(sk_der3)

    valid_maxima = []

    for peak in peaks:
        if sk_der3[peak] > sk_der1[peak]:
            valid_maxima.append(peak)

        if len(valid_maxima) >= N:
            break

    return valid_maxima


def read_mem_file(filename, name=None):
    data_dictionary = {}
    times = []


    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            try:
                d = json.loads(line)
            except:
                continue
            key = list(d.keys())[0]
            values = d[key]
            if len(data_dictionary) == 0:
                data_dictionary = {key: list() for key in values.keys()}
                data_dictionary[MU] = []
            times.append(datetime.strptime(key, '%Y-%m-%d %H:%M:%S.%f'))
            data_dictionary[MU].append((int(values["total"]) - int(values["free"])))
            for k in data_dictionary.keys():
                v = values.get(k, None)
                if v is not None:
                    data_dictionary[k].append(int(v))

    stats = {key: MemoryPlotStat(key, data) for key, data in data_dictionary.items()}

    time_seconds = np.array([(t - times[0]).total_seconds() for t in times])

    if name is None:
        name = filename

    return MemoryDataSet(name, time_seconds, stats, times[0], times[-1])


def mem_stat_string_builder(stats):
    if stats is None or len(stats) == 0:
        return ""
    max_length = max(len(stat) for stat in stats)

    sb = ""
    for i, stat in enumerate(stats):
        sb += f"{stat:<{max_length}}\t"

        if (i + 1) % 4 == 0:
            sb += "\n"
    return sb


def add_filter_handler(mpg: MemoryPlotGenerator, *args):
    if len(args) == 0:
        print(mem_stat_string_builder(mpg.data_sets[0].filters))
        return
    mpg.add_filter(*args)

def remove_filter_handler(mpg: MemoryPlotGenerator, *args):
    if len(args) == 0:
        print(mem_stat_string_builder(mpg.data_sets[0].filters))
        return
    mpg.remove_filter(*args)



def list_filters_handler(mpg: MemoryPlotGenerator, *_):
    stats = mpg.data_sets[0].stat_names()
    print(mem_stat_string_builder(stats))



def help_handler(_):
    print("Commands are:")
    for v in commands.keys():
        print("\t-", v)

def clear_filters_handler(mpg: MemoryPlotGenerator, *_):
    mpg.clear_filter()

def show_plot_handler(mpg: MemoryPlotGenerator):
    try:
        mpg.close_plot()
    except:
        pass

    mpg.show_plot()


commands = {
    "+f": add_filter_handler,
    "-f": remove_filter_handler,
    "f": list_filters_handler,
    "h": help_handler,
    "cf": clear_filters_handler,
    "s": show_plot_handler,

}


def main():
    args = sys.argv[1:]
    if len(args) < 1 or len(args) > 2:
        print("Unsure how to parse!", file=sys.stderr)
        return

    filename = args[0]

    second_filename = args[1] if len(args) == 2 else None

    stats = (MU, "buffers", "cached", "swapCache", "active", "inActive", "swapTotal", "swapFree", "zswap",
             'zswapped', 'dirty', 'writeback', 'pagesAnon', 'pageMapped', 'kernelStack', 'pageTables',
             'bounce', 'vmallocChunk', 'perCPU')


    base_path = "/home/duncan/Development/Uni/Thesis/Data/kernel/"
    base_path2 = "/home/duncan/Development/Uni/Thesis/Data/user_stack/results/"

    print("Reading memory data...")

    # mds1 = read_mem_file(base_path + "kernel_stack.json", "Kernel Stack 2Kb allocations")
    # mds2 = read_mem_file(base_path + "stack_exhaust1.json", "se1")
    # mds3 = read_mem_file(base_path2 + "stack_allocations1.json", "sa2")
    # mds4 = read_mem_file(base_path2 + "stack_allocations2.json", "sa3")
    # mds5 = read_mem_file(base_path2 + "stack_allocations3.json", "User Stack")
    # mpg5 = MemoryPlotGenerator(mds5).add_filter(MU, "cached", "buffers")
    # mpg5.compile_to_html("../docs/stack/total_memory_user.html")

    mds2 = read_mem_file(base_path + "kernel_allocations4.json", "re-insmod")
    mds1 = read_mem_file(base_path + "kernel_allocations6.json")

    mds2.append_data_set(mds1)

    print(mem_stat_string_builder(mds2.stat_names()))

    print(f"\nProcessed data ({filename}):")
    print(f" - Number of points collected: {len(mds2.time)}")
    print(f" - Start time: {mds2.start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f" - End time: {mds2.end_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f" - Duration (Seconds): {(mds2.end_time - mds2.start_time).total_seconds()}")


    mpg = MemoryPlotGenerator(mds2).add_filter("slab")

    mpg.show_plot()

    # mpg.compile_to_html("../docs/kernel/SlabReins.html")

    # filenames_go = [("gooutput_1.json", "Go Memory Usage (T1)"),
    #              ("gooutput_2.json", "Go Memory Usage (T2)"),
    #              ("gooutput_4.json", "Go Memory Usage (T4)"),
    #              ("gooutput_8.json", "Go Memory Usage (T8)"),
    #              ("gooutput_16.json", "Go Memory Usage (T16)"),
    #              ("gooutput_32.json", "Go Memory Usage (T32)"),
    #              ("gooutput_64.json", "Go Memory Usage (T64)"),
    #              ]
    #
    # filenames_c = [("coutput_1.json", "C Memory Usage (T1)"),
    #                 ("coutput_2.json", "C Memory Usage (T2)"),
    #                 ("coutput_4.json", "C Memory Usage (T4)"),
    #                 ("coutput_8.json", "C Memory Usage (T8)"),
    #                 ("coutput_16.json", "C Memory Usage (T16)"),
    #                 ("coutput_32.json", "C Memory Usage (T32)"),
    #                 ("coutput_64.json", "C Memory Usage (T64)"),
    #                 ]
    # ds1 = []
    # for fname, name, in filenames_c:
    #     ds1.append(read_mem_file(base_path + fname, name))
    #
    # ds2 = []
    # for fname, name, in filenames_go:
    #     ds2.append(read_mem_file(base_path + fname, name))
    #
    # # print(ds[0].stats["p_size"])
    # # print(ds[0].stat_names())
    # ds2[0].cut_end_time(39.56)
    # # ds2[1].cut_end_time(19.85)
    # # ds2[2].cut_end_time(10.1)
    # # ds2[3].cut_end_time(5.1)
    # # ds2[4].cut_end_time(2.88)
    # # ds2[5].cut_end_time(2.14)
    # ds2[6].cut_end_time(2.13)
    #
    # ds1[0].cut_end_time(38.67)
    # # ds1[1].cut_end_time(29.70)
    # # ds1[2].cut_end_time(17.4)
    # # ds1[3].cut_end_time(9.5)
    # # ds1[4].cut_end_time(5.12)
    # # ds1[5].cut_end_time(3.38)
    # ds1[6].cut_end_time(2.6)
    #
    # new_ds = [ds2[0], ds2[6], ds1[0], ds1[6]]
    # reduce = lambda x: [v /1024 for v in x]
    # for ds in new_ds:
    #     ds.apply_func(reduce)
    #
    # mpg = MemoryPlotGenerator(ds1[6], ds2[6], ds1[0], ds2[0]).add_filter('p_size')
    # mpg.y_label = "Memory Used (Mb)"
    # mpg.title = "Memory Used (DS3)"
    # mpg.show_plot()








if __name__ == '__main__':
    main()
