import os

from matplotlib import pyplot as plt
import numpy as np


def parse_true_csv(file_path):
    sep = ","
    with open(file_path, 'r') as reader:
        header_line = reader.readline().strip()
        data_line = reader.readline().strip()
        headers = header_line.split(sep)
        data = data_line.split(sep)
        zipped_data = zip(headers, data)
        result = {}
        for header, data in zipped_data:
            result[header] = float(data)

        return result


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
    parameter_map = {"alpha": r"$\alpha$", "beta": r"$\beta$"}
    # figure settings
    font_size = 14
    plt.rcParams['font.family'] = 'Helvetica'
    plt.rc('font', size=font_size)
    plt.rc('axes', titlesize=font_size)
    plt.rcParams['figure.figsize'] = (4.5, 4)
    plt.rcParams['figure.dpi'] = 300
    # process files
    file_range = range(1, 101)
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
    true_alphas = [x["alpha"] for x in true]
    true_betas = [x["beta"] for x in true]
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
        plt.title("Tree length error (binary)")
    elif mode == 1:
        z = hpd_range
        plt.title("Tree length HPD (binary)")
    else:
        z = color_values
        plt.title("Tree length coverage (binary)")
    plt.scatter(x=true_alphas, y=true_betas, c=z, s=20, alpha=0.5)
    if mode < 2:
        plt.set_cmap("viridis_r")
        plt.colorbar()
        print("Max: %f" % max(z))
    # color bar limits
    if mode == 0:
        plt.clim(0, 13)
    else:
        plt.clim(0, 14.1)
    plt.xlabel("Simulated " + parameter_map["alpha"])
    plt.ylabel("Simulated " + parameter_map["beta"])
    x_range = max(true_alphas) - min(true_alphas)
    y_range = max(true_betas) - min(true_betas)
    plt.ylim([y_range * -0.05, max(true_betas) * 1.05])
    plt.xlim([x_range * -0.05, max(true_alphas) * 1.05])
    xstep = x_range / 2
    ystep = y_range / 2
    plt.xticks([round(x, 2) for x in np.arange(0, max(true_alphas) + xstep / 2, xstep)])
    plt.yticks([round(x, 2) for x in np.arange(0, max(true_betas) + ystep / 2, ystep)])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.tight_layout()
    mode_options = {0: "mean", 1: "HPD", 2: "cov"}
    output_path = "../figures/binary_treelength_error_%s.pdf" % mode_options[mode]
    plt.savefig(output_path)
    print("figure saved: %s" % os.path.abspath(output_path))


# binary error model
stats_format = "../stats/binary_yule_no_error_n30_L400_%d_stats.log"
true_format = "../data/binary_yule_%d_true.csv"
plot_figs(stats_format, true_format, mode=0)
plot_figs(stats_format, true_format, mode=1)
plot_figs(stats_format, true_format, mode=2)
