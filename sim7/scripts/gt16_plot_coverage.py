import os

from matplotlib import pyplot as plt
import numpy as np
import dendropy
from dendropy.calculate import treemeasure


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


def translate_all_stats_logs(filepath, indices):
    for i in indices:
        translate_stats_log(filepath % i)

def translate_headers(headers):
    translate_map = {
        "pi_0": "pi.0",
        "pi_1": "pi.1",
        "pi_2": "pi.2",
        "pi_3": "pi.3",
        "pi_4": "pi.4",
        "pi_5": "pi.5",
        "pi_6": "pi.6",
        "pi_7": "pi.7",
        "pi_8": "pi.8",
        "pi_9": "pi.9",
        # ...
        "pi_10": "pi.a",
        "pi_11": "pi.b",
        "pi_12": "pi.c",
        "pi_13": "pi.d",
        "pi_14": "pi.e",
        # ...
        "pi_15": "pi.f",
        "rates_0": "rates.AC",
        "rates_1": "rates.AG",
        "rates_2": "rates.AT",
        "rates_3": "rates.CG",
        "rates_4": "rates.CT",
        "rates_5": "rates.GT",
        "T.height": "treeheight", 
        "T.treeLength": "treelength"
    }

    for key in translate_map:
        if key in headers:
            val = translate_map[key]
            idx = headers.index(key)
            # print("Translate %s to %s" % (key, val))
            headers[idx] = val

def calc_stats(filename, burnin=0, sample_num=1):
    tree_stats = {}
    calc_samples = 0
    for tree_idx, tree in enumerate(dendropy.Tree.yield_from_files(
            files=[filename],
            schema="nexus")):
        if tree_idx >= burnin and tree_idx % sample_num == 0:
            tree_stats["treelength"]= tree.length()
            tree_stats["treeheight"] = tree.max_distance_from_root()
        break

    return tree_stats


def parse_true_csv(file_path):
    sep = "\t"
    result = {}
    with open(file_path, 'r') as reader:
        header_line = reader.readline().strip()
        data_line = reader.readline().strip()
        headers = header_line.split(sep)
        #print(headers)
        translate_headers(headers)
        data = data_line.split(sep)
        zipped_data = zip(headers, data)
        
        for header, data in zipped_data:
            result[header] = float(data)

    aux_path = file_path[:-4] + "_T.trees"
    aux_res = calc_stats(aux_path)

    return result | aux_res


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
            # print(headers)
            translate_headers(headers)
            zipped_data = zip(headers, items)
            tmp = {}
            for header, data in zipped_data:
                tmp[header] = float(data)
            result[trace] = tmp

    return result


def plot_figs(stats_path, true_path, parameter_list, ep, dt, indices, suffix):
    true = []
    mean = []
    hdp95lower = []
    hdp95upper = []
    ess = []
    
    # translate_all_true_logs(true_path, indices)
    # # translate stats logs
    # translate_all_stats_logs(stats_path, indices)
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
        "theta": r"$\theta$"
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
        mean_values = [x[parameter] for x in mean]
        lowers = [x[parameter] for x in hdp95lower]
        uppers = [x[parameter] for x in hdp95upper]
        
        if parameter == "delta":
            true_values = [dt] * len(mean_values) 
        elif parameter == "epsilon":
            true_values = [ep] * len(mean_values)
        else:
            true_values = [x[parameter] for x in true]
        
        # map colors
        color_list = {True: 'c', False: 'r'}
        colors_boolean = [lowers[i] <= true_values[i] <= uppers[i] for i in range(len(true_values))]
        color_values = [color_list[x] for x in colors_boolean]

        count_cov = 0.0
        for item in colors_boolean:
            if item:
                count_cov += 1.0
        print("true path: %s" % true_path)
        print(count_cov / len(colors_boolean))

        # begin plotting
        plt.clf()
        line_width = 3
        alpha = 0.2
        ax = plt.subplot(111)
        
        if parameter == "treeheight":
            plt.plot(true_values, mean_values, 'k.', ms=2, zorder=2)
            plt.vlines(true_values, ymin=lowers, ymax=uppers, colors=color_values, alpha=alpha, lw=line_width, zorder=1)
            plt.ylim([0, 1.05])
            plt.xlim([0, 1.05])
            plt.xticks(np.arange(0, 3.1, 1.0))
            plt.yticks(np.arange(0, 3.1, 1.0))
            plt.plot([0, 3], [0, 3], 'k-', lw=0.5, label="x = y", zorder=10)
        elif parameter == "treelength":
            plt.plot(true_values, mean_values, 'k.', ms=2, zorder=2)
            plt.vlines(true_values, ymin=lowers, ymax=uppers, colors=color_values, alpha=alpha, lw=line_width, zorder=1)
            plt.ylim([0, 10.5])
            plt.xlim([0, 10.5])
            plt.xticks(range(0, 11, 2))
            plt.yticks(range(0, 11, 2))
            plt.plot([0, 10], [0, 10], 'k-', lw=0.5, label="x = y", zorder=10)
        elif parameter == "delta" or parameter == "epsilon":
            plt.plot(range(len(lowers)), mean_values, 'k.', ms=2, zorder=2)
            plt.vlines(range(len(lowers)), ymin=lowers, ymax=uppers, colors=color_values, alpha=alpha, lw=line_width, zorder=1)
            plt.plot([0, len(lowers)], [true_values[0], true_values[0]], 'k-', lw=0.5)
            plt.ylabel("Estimated " + parameter_map[parameter])
            plt.xlabel("Experiment index")
            plt.title("True " + parameter_map[parameter] + " = " + str(true_values[0]))
        else:
            plt.plot(true_values, mean_values, 'k.', ms=2, zorder=2)
            plt.vlines(true_values, ymin=lowers, ymax=uppers, colors=color_values, alpha=alpha, lw=line_width, zorder=1)
            y1 = min(lowers)
            y2 = max(uppers)
            x1 = min(true_values)
            x2 = max(true_values)
            plt.plot([x1, x2], [x1, x2], 'k-', lw=0.5, label="x = y", zorder=10)

        if parameter.startswith("tree"):
            plt.ylabel("Estimated " + parameter_map[parameter])
            plt.xlabel("True " + parameter_map[parameter])
            plt.title(parameter_map[parameter].capitalize())
        else:
            plt.ylabel("Estimated " + parameter_map[parameter])
            plt.xlabel("True " + parameter_map[parameter])
            plt.title(parameter_map[parameter])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tight_layout()

        output_path = "../figures/gt16_EM_" + parameter.lower().replace(".", "_") + suffix + ".pdf"
        plt.savefig(output_path)
        print("figure saved: %s" % os.path.abspath(output_path))


# gt16 simulation 3
parameters = ["delta", "epsilon", "theta", "pi.0", "pi.1", "pi.2", "pi.3",
              "pi.4", "pi.5", "pi.6", "pi.7", "pi.8", "pi.9",
              "pi.a", "pi.b", "pi.c", "pi.d", "pi.e", "pi.f", 
              "rates.AC", "rates.AG", "rates.AT", "rates.CG", "rates.CT", "rates.GT",
              "treeheight", "treelength"
              ]

# delta files
ep = 0.001
# file indices
fileno = list(range(10, 20)) 
print("repeats: %d" % len(fileno))
for dt in [10, 25, 50, 80]: 
    stats_format = "../stats/gt16/gt16_delta_" + str(dt) + "_%d_stats.log"
    true_format = "../data/gt16_delta/gt16_delta_" + str(dt) + "_%d_true.log"
    plot_figs(stats_format, true_format, parameters, ep, dt/100.0, fileno, "_dt_%d" % dt)

# epsilon files
dt = 0.5
fileno = list(range(10, 20))
print("repeats: %d" % len(fileno))
for ep in [0.1, 1, 5, 10]:
    stats_format = "../stats/gt16/gt16_epsilon_" + str(ep) + "_%d_stats.log"
    true_format = "../data/gt16_epsilon/gt16_epsilon/gt16_epsilon_" + str(ep) + "_%d_true.log"
    if ep < 1:
        plot_figs(stats_format, true_format, parameters, ep/100.0, dt, fileno, "_ep_%.1f" % ep)
    else:
        plot_figs(stats_format, true_format, parameters, ep/100.0, dt, fileno, "_ep_%d" % ep)

