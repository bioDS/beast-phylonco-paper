import collections
import os
import pickle

import dendropy
from dendropy.calculate import treemeasure
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch
from matplotlib.pyplot import figure


def calc_stats(filename, burnin=0, sample_num=1):
    tree_stats = collections.defaultdict(list)
    calc_samples = 0
    for tree_idx, tree in enumerate(dendropy.Tree.yield_from_files(
            files=[filename],
            schema="nexus")):
        if tree_idx >= burnin and tree_idx % sample_num == 0:
            tree_stats["treelength"].append(tree.length())
            tree_stats["treeheight"].append(tree.max_distance_from_root())
            tree_stats["B1"].append(treemeasure.B1(tree))
            tree_stats["colless"].append(treemeasure.colless_tree_imbalance(tree))
            tree_stats["PBH"].append(treemeasure.pybus_harvey_gamma(tree))
            tree_stats["sackin"].append(treemeasure.sackin_index(tree))
            tree_stats["treeness"].append(treemeasure.treeness(tree))
            calc_samples = calc_samples + 1
    print("File: %s" % filename)
    print("Calculated samples: %d" % calc_samples)
    return tree_stats


def get_stat(filename, key):
    tree_stats = calc_stats(filename)
    return tree_stats[key]


# append tree height and tree length stats
def append_tree_stats(tree_log, true_log):
    if os.path.exists(true_log + ".orig"):
        return
    os.rename(true_log, true_log + ".orig")
    reader = open(true_log + ".orig", "r")
    writer = open(true_log, "w")
    in_header = True
    sep = "\t"
    append_height = True
    append_length = True
    stats = calc_stats(tree_log)
    for line in reader:
        items = line.strip().split(sep)
        writer.write(line.strip())
        if in_header:
            if "treeheight" in items:
                append_height = False
            else:
                writer.write(sep + "treeheight")
            if "treelength" in items:
                append_length = False
            else:
                writer.write(sep + "treelength")
            writer.write("\n")
            in_header = False
        else:
            if append_height:
                writer.write(sep + str(stats["treeheight"][0]))
            if append_length:
                writer.write(sep + str(stats["treelength"][0]))
            writer.write("\n")
    reader.close()
    writer.close()


def append_stats_all():
    for i in range(100):
        tree_file = "../data/gt16CoalErrModel_%d_true_ψ.trees" % i
        true_file = "../data/gt16CoalErrModel_%d_true.log" % i
        append_tree_stats(tree_file, true_file)


def get_num_samples(filename):
    pattern = "tree STATE_"
    num_samples = 0
    with open(filename) as f:
        for line in f:
            if line.startswith(pattern):
                num_samples = num_samples + 1
    return num_samples


def get_stats_from_tree(filename, burnin=0.1, sample_num=1):
    n = get_num_samples(filename)
    print("Total samples: %d" % n)
    tree_stats = calc_stats(filename, n * burnin, sample_num)
    with open(filename + ".pkl", 'wb') as f:
        pickle.dump(tree_stats, f)


def load_stats(filename):
    with open(filename + ".pkl", 'rb') as handle:
        data = pickle.load(handle)
    return data


def plot_fig(parameter, data_name, data):
    label_map = {"treeness": "Treeness", "PBH": "Gamma statistic",
                 "treeheight": "Tree height", "treelength": "Tree length"}
    combined_data = [data[0][parameter], data[1][parameter],
                     data[2][parameter], data[3][parameter]]
    colors = ["#F8766D", "#00BFC4", "#F8766D", "#00BFC4"]
    # begin plotting
    fig = figure(figsize=(4.5, 4.5), dpi=300)
    ax = sns.violinplot(data=combined_data, palette=colors,
                        saturation=1,
                        linewidth=0, inner=None)
    # plt.setp(ax.collections, alpha=1.0)
    locs, labels = plt.xticks()
    plt.ylabel(label_map[parameter])
    # add legend
    legend_elements = [Patch(facecolor="white", label='Models'),
                       Patch(facecolor=colors[0], label='GT16 EM'),
                       Patch(facecolor=colors[1], label='GT16')]
    legend = ax.legend(handles=legend_elements,
                       bbox_to_anchor=(0.5, -0.25), loc="lower center", borderaxespad=0.05,
                       ncol=3)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xticks([0.5, 2.5], [data_name, data_name + ' outgroup'])
    output_path = "../figures/" + data_name + "_" + parameter + ".pdf"
    plt.savefig(output_path,
                bbox_inches='tight',
                bbox_extra_artists=(legend,))
    print("figure saved: %s" % os.path.abspath(output_path))


# plot settings
font = {'family': 'helvetica',
        'size': '14'}
plt.rc('font', **font)  # pass in the font dict as kwargs
plt.rcParams["patch.force_edgecolor"] = False
parameters = ["treeness", "PBH", "treeheight", "treelength"]

# E15 dataset
data_name = "E15"
file1 = "../beast/E15_rskycoal_em_fast.trees"
file2 = "../beast/E15_rskycoal_fast.trees"
file3 = "../beast/E15_rskycoal_em_outgroup.trees"
file4 = "../beast/E15_rskycoal_outgroup.trees"

# get stats only need to be run once
if not os.path.exists(file1):
    get_stats_from_tree(file1)

if not os.path.exists(file2):
    get_stats_from_tree(file2)

if not os.path.exists(file3):
    get_stats_from_tree(file3)

if not os.path.exists(file4):
    get_stats_from_tree(file4)

# load stats
data1 = load_stats(file1)
data2 = load_stats(file2)
data3 = load_stats(file3)
data4 = load_stats(file4)

# plot tree stats
for p in parameters:
    plot_fig(p, data_name, [data1, data2, data3, data4])
