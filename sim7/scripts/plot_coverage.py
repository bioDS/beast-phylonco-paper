import os

from matplotlib import pyplot as plt
import numpy as np


def split_true_log(filename):
    results = {}
    with open(filename, "r") as fp:
        header_line = fp.readline()
        for data_line in fp:
            idx = data_line.split(",")[0]
            if idx not in results:
                results[idx] = []

            results[idx].append(data_line)

        for key in results:
            suffix = "_true.csv"
            output_path = filename.replace(suffix, "_%s%s" % (key, suffix))
            with open(output_path, "w") as wfp:
                wfp.write(header_line)
                for item in results[key]:
                    wfp.write(item)



def translate_all_stats_logs(stats_log, indices):
    var_map = {
        "subsModel.lambda": "lambda",
        "error.alpha": "alpha",
        "error.beta": "beta",
        "yule.birthrate": "birthrate",
        "tree.treeLength": "treelength",
        "tree.height": "treeheight",
        "treeLikelihood": "likelihood"
    }
    for i in indices:
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


def plot_figs(stats_path, true_path, parameter_list, indices, a_param, b_param, prefix):
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
    for fileid in indices:
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

        # get true error values
        if parameter == "alpha":
            true_values = [a_param] * len(mean_values)
        elif parameter == "beta":
            true_values = [b_param] * len(mean_values)
        
        # map colors
        color_list = {True: 'c', False: 'r'}
        colors_boolean = [lowers[i] <= true_values[i] <= uppers[i] for i in range(len(true_values))]
        color_values = [color_list[x] for x in colors_boolean]

        counter = 0
        for i in colors_boolean:
            if i:
                counter += 1
        coverage = 100 * counter / len(colors_boolean)
        print("%d" % int(coverage))
        
        # begin plotting
        plt.clf()
        line_width = 3
        alpha = 0.2
        ax = plt.subplot(111)

        if parameter == "alpha" or parameter == "beta":
            plt.plot(range(len(mean_values)), mean_values, 'k.', ms=2, zorder=2)
            plt.vlines(range(len(mean_values)), colors=color_values,
                ymin=lowers, ymax=uppers, alpha=alpha, lw=line_width, zorder=1)
            plt.plot([0, len(mean_values)], [true_values[0], true_values[0]], 'k-', lw=0.5, zorder=3)
            plt.xlabel("Experiment index")
            plt.ylabel("Estimated " + parameter_map[parameter])
            plt.title("True " + parameter_map[parameter] + " = " + str(true_values[0]))
        else:
            plt.plot(true_values, mean_values, 'k.', ms=2, zorder=2)
            plt.vlines(true_values, colors=color_values,
                ymin=lowers, ymax=uppers, alpha=alpha, lw=line_width, zorder=1)
            xmin = min(true_values)
            xmax = max(true_values)
            plt.plot([xmin, xmax], [xmin, xmax], 'k-', lw=0.5, zorder=10)
            plt.xlabel("True " + parameter_map[parameter])
            plt.ylabel("Estimated " + parameter_map[parameter])
            plt.title(parameter_map[parameter].capitalize())
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tight_layout()
        output_path = "../figures/binary_%s_EM_%s.pdf" % (prefix, parameter.replace(".", "_"))
        plt.savefig(output_path)
        print("figure saved: %s" % os.path.abspath(output_path))


# simulation 1
# binary error model
indices = range(1, 11)
parameters = ["lambda", "treeheight", "treelength", "alpha", "beta", "birthrate"]

alpha = 0.001
for beta in [0.1, 0.25, 0.5, 0.6]:
    prefix = str(int(beta*100))
    stats_format = "../stats/binary/binary_beta_" + prefix + "_%d_stats.log"
    true_format = "../data/binary_beta/binary_beta_" + prefix + "_true.csv"
    split_true_log(true_format)
    translate_all_stats_logs(stats_format, indices)
    true_format = "../data/binary_beta/binary_beta_" + prefix + "_%d_true.csv"
    plot_figs(stats_format, true_format, parameters, indices, alpha, beta, "b" + prefix)

beta = 0.5
for alpha in [0.001, 0.01, 0.05, 0.1]:
    prefix = str(int(alpha*100))
    if alpha < 0.01:
        prefix = "0.1"
    stats_format = "../stats/binary/binary_alpha_" + prefix + "_%d_stats.log"
    true_format = "../data/binary_alpha/binary_alpha_" + prefix + "_true.csv"
    split_true_log(true_format)
    translate_all_stats_logs(stats_format, indices)
    true_format = "../data/binary_alpha/binary_alpha_" + prefix + "_%d_true.csv"
    plot_figs(stats_format, true_format, parameters, indices, alpha, beta, "a" + prefix)
