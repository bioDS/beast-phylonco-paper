import os

from matplotlib import pyplot as plt
import numpy as np


def translate_stats_log(file_path):
    translate_map = {
        "psi.height": "treeheight",
        "psi.treeLength": "treelength"
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


def translate_all_stats_logs(filepath):
    for i in range(100):
        translate_stats_log(filepath % i)


def parse_true_csv(file_path):
    sep = "\t"
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


def plot_figs(stats_path, true_path, parameter_list):
    true = []
    mean = []
    hdp95lower = []
    hdp95upper = []
    ess = []
    # translate stats logs
    translate_all_stats_logs(stats_path)
    # convert parameters to math characters
    parameter_map = {
        "delta": r"$\delta$",
        "epsilon": r"$\epsilon$",
        "treeheight": "tree height",
        "treelength": "tree length",
        "pi.0": r"$\pi_{AA}$",
        "pi.1": r"$\pi_{AC}$",
        "pi.2": r"$\pi_{AG}$",
        "pi.3": r"$\pi_{AT}$",
        "pi.4": r"$\pi_{CA}$",
        "pi.5": r"$\pi_{CC}$",
        "pi.6": r"$\pi_{CG}$",
        "pi.7": r"$\pi_{CT}$",
        "pi.8": r"$\pi_{GA}$",
        "pi.9": r"$\pi_{GC}$",
        "pi.a": r"$\pi_{GG}$",
        "pi.b": r"$\pi_{GT}$",
        "pi.c": r"$\pi_{TA}$",
        "pi.d": r"$\pi_{TC}$",
        "pi.e": r"$\pi_{TG}$",
        "pi.f": r"$\pi_{TT}$",
        "rates.AC": r"$r_{AC}$",
        "rates.AG": r"$r_{AG}$",
        "rates.AT": r"$r_{AT}$",
        "rates.CG": r"$r_{CG}$",
        "rates.CT": r"$r_{CT}$",
        "rates.GT": r"$r_{GT}$",
        "Theta": r"$\theta$"
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
    for fileid in range(100):
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
            plt.xticks(np.arange(0, 3.1, 1.0))
            plt.yticks(np.arange(0, 3.1, 1.0))
            plt.plot([0, 3], [0, 3], 'k-', lw=0.5, label="x = y", zorder=10)
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
        if parameter.startswith("tree"):
            plt.title(parameter_map[parameter].capitalize())
        else:
            plt.title(parameter_map[parameter])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tight_layout()

        output_path = "../figures/gt16_" + parameter.lower().replace(".", "_") + ".pdf"
        plt.savefig(output_path)
        print("figure saved: %s" % os.path.abspath(output_path))


# gt16 simulation 5
parameters = ["treeheight", "treelength", "Theta", "pi.0", "pi.1", "pi.2", "pi.3",
              "pi.4", "pi.5", "pi.6", "pi.7", "pi.8", "pi.9", "pi.a", "pi.b", "pi.c", "pi.d", "pi.e",
              "pi.f", "rates.AC", "rates.AG", "rates.AT", "rates.CG", "rates.CT", "rates.GT"]
stats_format = "../stats/gt16_coal_no_error_n16_L200_%d_stats.log"
true_format = "../data/gt16CoalErrModel_%d_true.log"
plot_figs(stats_format, true_format, parameters)

