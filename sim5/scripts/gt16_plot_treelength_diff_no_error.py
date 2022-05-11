import os

from matplotlib import pyplot as plt
import numpy as np


def parse_true_csv(file_path):
    with open(file_path, 'r') as fp:
        sep = "\t"
        header_line = fp.readline().strip()
        data_line = fp.readline().strip()
        headers = header_line.split(sep)
        data = data_line.split(sep)
        zipped_data = zip(headers, data)
        result = {}
        for header, data in zipped_data:
            result[header] = float(data)

        return result


def translate_stats_log(file_path):
    translate_map = {
        "psi.height": "treeheight",
        "psi.treeLength": "treelength",
    }
    if os.path.exists(file_path + ".orig"):
        return
    os.rename(file_path, file_path + ".orig")
    writer = open(file_path, 'w')
    with open(file_path + ".orig", 'r') as reader:
        header_line = reader.readline().strip()
        headers = header_line.split('\t')
        for i in range(len(headers)):
            if headers[i] in translate_map:
                headers[i] = translate_map[headers[i]]
        writer.write("\t".join(headers) + "\n")
        for data_line in reader:
            writer.write(data_line)
    writer.close()


def parse_stats_log(file_path):
    with open(file_path, 'r') as reader:
        result = {}
        header_line = reader.readline().strip()
        headers = header_line.split('\t')[1:]

        for data_line in reader:
            data_line = data_line.strip()
            items = data_line.split('\t')
            trace = items[0]
            if trace == "mode":
                continue

            items = items[1:]

            zipped_data = zip(headers, items)
            tmp = {}
            for header, data in zipped_data:
                tmp[header] = float(data)

            result[trace] = tmp

    return result


# plot error parameters colored by tree length mean difference or hpd size
# mode 0 = mean - true value
# mode 1 = HPD size
def plot_figs(stats_path, true_path, mode):
    true = []
    mean = []
    hdp95lower = []
    hdp95upper = []
    # convert parameters to math characters
    parameter_map = {"delta": r"$\delta$", "epsilon": r"$\epsilon$"}
    # figure settings
    font_size = 14
    plt.rcParams['font.family'] = 'Helvetica'
    plt.rc('font', size=font_size)
    plt.rc('axes', titlesize=font_size)
    plt.rcParams['figure.figsize'] = (4.5, 4)
    plt.rcParams['figure.dpi'] = 300
    # process files
    file_range = range(100)
    for fileid in file_range:
        stats_file = stats_path % fileid
        true_file = true_path % fileid
        stats_data = parse_stats_log(stats_file)
        true_data = parse_true_csv(true_file)
        mean.append(stats_data['mean'])
        hdp95lower.append(stats_data['HPD95.lower'])
        hdp95upper.append(stats_data['HPD95.upper'])
        true.append(true_data)
    # plot parameters
    parameter = "treelength"
    # get values
    true_values = [x[parameter] for x in true]
    mean_values = [x[parameter] for x in mean]
    lowers = [x[parameter] for x in hdp95lower]
    uppers = [x[parameter] for x in hdp95upper]
    true_deltas = [x["delta"] for x in true]
    true_epsilons = [x["epsilon"] for x in true]
    # map colors
    color_list = {True: 'c', False: 'r'}
    colors_boolean = [lowers[i] <= true_values[i] <= uppers[i] for i in range(len(true_values))]
    color_values = [color_list[x] for x in colors_boolean]
    # calculate values
    total_files = len(file_range)
    hpd_range = [uppers[x] - lowers[x] for x in range(total_files)]
    mean_hpd = sum(hpd_range) / total_files  # mean of HPD range
    coverage = 100.0 * color_values.count('c') / total_files
    # print("mean hpd size: %f" % mean_hpd)
    # print("coverage: %f" % coverage)
    # begin plotting
    plt.clf()
    ax = plt.subplot(111)
    if mode == 0:
        z = np.abs(np.subtract(true_values, mean_values))
        plt.title("Tree length error (GT16)")
    elif mode == 1:
        z = hpd_range
        plt.title("Tree length HPD (GT16)")
    else:
        z = color_values
        plt.title("Tree length coverage (GT16 EM)")
    plt.scatter(x=true_deltas, y=true_epsilons, c=z, s=20, alpha=0.5)
    if mode < 2:
        plt.set_cmap("viridis_r")
        plt.colorbar()
        print("color max value: %f" % max(z))
        # color bar limits
        if mode == 0:
            plt.clim(0, 8.5)
        else:
            plt.clim(0, 4.0)
    plt.xlabel("Simulated " + parameter_map["delta"])
    plt.ylabel("Simulated " + parameter_map["epsilon"])
    xymax = max(max(true_deltas), max(true_epsilons))
    plt.ylim([0, xymax * 1.05])
    plt.xlim([0, xymax * 1.05])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.tight_layout()
    mode_options = {0: "mean", 1: "HPD", 2: "cov"}
    output_path = "../figures/gt16_treelength_error_%s.pdf" % mode_options[mode]
    plt.savefig(output_path)
    print("figure saved: %s" % os.path.abspath(output_path))


def translate_all_stats_logs():
    for i in range(100):
        translate_stats_log("../stats/gt16_coal_no_error_n16_L200_%d_stats.log" % i)


# gt16 error model
translate_all_stats_logs()
stats_format = "../stats/gt16_coal_no_error_n16_L200_%d_stats.log"
true_format = "../data/gt16CoalErrModel_%d_true.log"
plot_figs(stats_format, true_format, mode=0)
plot_figs(stats_format, true_format, mode=1)
plot_figs(stats_format, true_format, mode=2)
