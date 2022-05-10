import collections
import os

import dendropy
from dendropy.calculate import treemeasure


def calc_stats(filename):
    tree_stats = collections.defaultdict(list)
    for tree_idx, tree in enumerate(dendropy.Tree.yield_from_files(
            files=[filename],
            schema="nexus")):
        tree_stats["treelength"].append(tree.length())
        tree_stats["treeheight"].append(tree.max_distance_from_root())
        tree_stats["B1"].append(treemeasure.B1(tree))
        tree_stats["colless"].append(treemeasure.colless_tree_imbalance(tree))
        tree_stats["PBH"].append(treemeasure.pybus_harvey_gamma(tree))
        tree_stats["sackin"].append(treemeasure.sackin_index(tree))
        tree_stats["treeness"].append(treemeasure.treeness(tree))
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


# append tree stats to all files in data *_true.log
append_stats_all()
