import os

from matplotlib import pyplot as plt
import numpy as np


def parse_true_csv(file_path, delimiter):
    with open(file_path, 'r') as reader:
        header_line = reader.readline().strip()
        data_line = reader.readline().strip()
        headers = header_line.split(delimiter)
        data = data_line.split(delimiter)
        zipped_data = zip(headers, data)
        result = {}
        for header, data in zipped_data:
            result[header] = float(data)

        return result


def scatter_hist(x, y, xtext, ytext, ax, ax_histx, ax_histy):
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)
    ax_histx.set_ylabel(xtext + " counts")
    ax_histy.set_xlabel(ytext + " counts")

    # scatter plot
    ax.scatter(x, y, color='lightgrey')
    ax.set_xlabel("Simulated values " + xtext)
    ax.set_ylabel("Simualted values " + ytext)

    xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
    xymin = min(np.min(np.abs(x)), np.min(np.abs(y)))
    binwidth = (xymax - xymin) / 50
    lim = (int(xymax/binwidth) + 1) * binwidth

    bins = np.arange(0, lim, step=binwidth)
    ax_histx.hist(x, bins=bins, color='c', alpha=0.7)
    ax_histy.hist(y, bins=bins, color='c', alpha=0.7, orientation='horizontal')


def plot_figs(true_path, filename, sep):
    parameter_list = ["delta", "epsilon"]
    # convert parameters for figure display
    parameter_map = {"delta": r"$\delta$", "epsilon": r"$\epsilon$"}

    # process files
    true = []
    for fileid in range(100):
        true_file = true_path % fileid
        true_data = parse_true_csv(true_file, delimiter=sep)
        true.append(true_data)

    # get true parameters
    x = [x[parameter_list[0]] for x in true]
    y = [x[parameter_list[1]] for x in true]

    # begin plotting
    plt.clf()
    left, width = 0.15, 0.6
    bottom, height = 0.15, 0.6
    spacing = 0.01

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]

    # figure settings
    font_size = 16
    fig = plt.figure(figsize=(8, 8))
    plt.rcParams['font.family'] = 'Helvetica'
    plt.rc('font', size=font_size)
    plt.rc('axes', titlesize=font_size)
    plt.rcParams['figure.dpi'] = 300

    ax = fig.add_axes(rect_scatter)
    ax_histx = fig.add_axes(rect_histx, sharex=ax)
    ax_histy = fig.add_axes(rect_histy, sharey=ax)

    param_text_x = parameter_map[parameter_list[0]]
    param_text_y = parameter_map[parameter_list[1]]
    scatter_hist(x, y, param_text_x, param_text_y, ax, ax_histx, ax_histy)

    plt.savefig(filename)
    print("figure saved: %s" % os.path.abspath(filename))


# plot gt16 error parameters
true_format = "../data/gt16CoalErrModel_%d_true.log"
output_name = "../figures/gt16_error_dist.pdf"
plot_figs(true_format, output_name, sep='\t')
