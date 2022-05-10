import os

from matplotlib import pyplot as plt
import numpy as np


def split_true_file(true_log):
    reader = open(true_log, "r")
    count = 1
    in_header = True
    header = ""
    for line in reader:
        items = line.split(",")
        if in_header:
            header = ",".join(items[0:5]) + "," + str(items[6]) + "," + str(items[5])
            in_header = False
        if str(count) == items[0]:
            write_log = true_log.replace("yule", "yule_%d" % count)
            writer = open(write_log, "w")
            writer.write(header + "\n")
            writer.write(",".join(items[0:5]) + "," + str(items[6]) + "," + str(items[5]) + "\n")
            writer.close()
            count = count + 1
    reader.close()


def translate_all_stats_logs(stats_log):
    var_map = {
        "subsModel.lambda": "lambda",
        "error.alpha": "alpha",
        "error.beta": "beta",
        "yule.birthrate": "birthrate",
        "tree.treeLength": "treelength",
        "tree.height": "treeheight",
        "treeLikelihood": "likelihood"
    }
    for i in range(1, 101):
        stats_file = stats_log % i
        temp_file = stats_file.replace(".log", "-temp.log")
        os.rename(stats_file, temp_file)
        reader = open(temp_file, "r")
        writer = open(stats_file, "w")
        in_header = True
        for line in reader:
            if in_header:
                header = line
                for x in var_map:
                    if x in header:
                        header = header.replace(x, var_map[x])
                line = header
                in_header = False
            writer.write(line)
        reader.close()
        writer.close()
        os.remove(temp_file)  # cleanup temp file


def parse_true_csv(file_path):
    with open(file_path, 'r') as fp:
        header_line = fp.readline().strip()
        data_line = fp.readline().strip()
        headers = header_line.split(',')
        data = data_line.split(',')
        zipped_data = zip(headers, data)
        result = {}
        for header, data in zipped_data:
            result[header] = float(data)

        return result


def parse_stats_log(file_path):
    with open(file_path, 'r') as fp:
        result = {}
        header_line = fp.readline().strip()
        headers = header_line.split('\t')[1:]

        for data_line in fp:
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


def plot_figs(stats_path, true_path, parameter_list):
    true = []
    mean = []
    hdp95lower = []
    hdp95upper = []
    ess = []
    # convert parameters to math characters
    parameter_map = {
        "lambda": r"$\lambda$",
        "alpha": r"$\alpha$",
        "beta": r"$\beta$",
        "birthrate": "birthrate",
        "treeheight": "tree height",
        "treelength": "tree length"
    }
    # figure settings
    font_size = 12
    width = 6.75 / 2
    plt.rcParams['font.family'] = 'Helvetica'
    plt.rc('font', size=font_size)
    plt.rc('axes', titlesize=font_size)
    plt.rcParams['figure.figsize'] = (width, width)
    plt.rcParams['figure.dpi'] = 300
    # process files
    for fileid in range(1, 101):
        stats_file = stats_path % fileid
        true_file = true_path % fileid
        stats_data = parse_stats_log(stats_file)
        true_data = parse_true_csv(true_file)
        mean.append(stats_data['mean'])
        hdp95lower.append(stats_data['HPD95.lower'])
        hdp95upper.append(stats_data['HPD95.upper'])
        ess.append(stats_data['ESS'])
        true.append(true_data)
    # plot parameters
    for parameter in parameter_list:
        # get values
        true_values = [x[parameter] for x in true]
        mean_values = [x[parameter] for x in mean]
        lowers = [x[parameter] for x in hdp95lower]
        uppers = [x[parameter] for x in hdp95upper]
        # map colors
        color_list = {True: 'c', False: 'r'}
        colors_boolean = [lowers[i] <= true_values[i] <= uppers[i] for i in range(len(true_values))]
        color_values = [color_list[x] for x in colors_boolean]
        # begin plotting
        plt.clf()
        line_width = 3
        alpha = 0.2
        ax = plt.subplot(111)
        plt.plot(true_values, mean_values, 'k.', ms=2, zorder=2)
        plt.vlines(true_values, ymin=lowers, ymax=uppers, colors=color_values, alpha=alpha, lw=line_width, zorder=1)
        if parameter == "treeheight":
            plt.ylim([0, 1.05])
            plt.xlim([0, 1.05])
            plt.xticks(np.arange(0, 1.1, 0.2))
            plt.yticks(np.arange(0, 1.1, 0.2))
            plt.plot([0, 1], [0, 1], 'k-', lw=0.5, label="x = y", zorder=10)
        elif parameter == "treelength":
            plt.ylim([0, 10.5])
            plt.xlim([0, 10.5])
            plt.xticks(range(0, 11, 2))
            plt.yticks(range(0, 11, 2))
            plt.plot([0, 10], [0, 10], 'k-', lw=0.5, label="x = y", zorder=10)
        else:
            y1 = min(lowers)
            y2 = max(uppers)
            x1 = min(true_values)
            x2 = max(true_values)
            plt.plot([x1, x2], [x1, x2], 'k-', lw=0.5, label="x = y", zorder=10)
        plt.xlabel("True " + parameter_map[parameter])
        plt.ylabel("Estimated " + parameter_map[parameter])
        plt.title(parameter_map[parameter].capitalize())
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tight_layout()
        output_path = "../figures/binary_EM_" + parameter.replace(".", "_") + ".pdf"
        plt.savefig(output_path)
        print("figure saved: %s" % os.path.abspath(output_path))


# simulation 1
# binary error model
parameters = ["lambda", "treeheight", "treelength", "alpha", "beta", "birthrate"]
stats_format = "../stats/binary_yule_n30_L400_%d_stats.log"
true_format = "../data/binary_yule_%d_true.csv"
translate_all_stats_logs(stats_format)
plot_figs(stats_format, true_format, parameters)
