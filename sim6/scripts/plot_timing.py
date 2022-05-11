import numpy as np
from matplotlib import pyplot as plt


SECONDS_PER_HOUR = 3600


def get_min_ess(filename):
    match_line = "ESS"
    handle = open(filename, 'r')
    res_ess = 0
    for line in handle:
        if line.startswith(match_line):
            words = line.split("\t")
            ess_list = []
            for j in range(len(words)):
                if j > 0:
                    ess = float(words[j])
                    ess_list.append(ess)
            res_ess = min(ess_list)
            break
    handle.close()
    return res_ess


def get_total_time(filename):
    match_line = "Total calculation time"
    time = 0.0
    handle = open(filename, 'r')
    for line in handle:
        if line.startswith(match_line):
            words = line.split(" ")
            time = float(words[3])
            units = words[4].strip("\n")
            if not units == "seconds":
                print("Warning: units is in %s!" % units)
            break
    handle.close()
    return time


def get_ess_time_stats(time_pattern, ess_pattern, num_taxa, num_sites, num_repeats = 10):
    time_list = []
    ess_list = []
    for i in range(num_repeats):
        time_log = time_pattern % (num_taxa, num_sites, i)
        time_seconds = get_total_time(time_log)
        ess_log = ess_pattern % (num_taxa, num_sites, i)
        min_ess = get_min_ess(ess_log)
        time_list.append(time_seconds)
        ess_list.append(min_ess)
    return time_list, ess_list


def get_ess_per_hour(time_seconds, ess_list):
    ess_per_hour = []
    for i in range(len(time_seconds)):
        time_hours = time_seconds[i] / SECONDS_PER_HOUR
        ess = ess_list[i]
        ess_per_hour.append(ess / time_hours)
    return ess_per_hour


num_taxa = 20
num_repeats = 10

# gt16 logs
gt16_time_log = "../beast/timing_gt16_screenlogs/gt16Coal_%s_taxa_%s_sites_%d.xml.screenlog"
gt16_ess_log = "../stats/timing_gt16_stats/gt16Coal_%s_taxa_%s_sites_%d_stats.log"

# gt16 error model logs
gt16_time_log_em = "../beast/timing_gt16_screenlogs_em/gt16CoalErrModelFast_%s_taxa_%s_sites_%d.xml.screenlog"
gt16_ess_log_em = "../stats/timing_gt16_stats_em/gt16CoalErrModelFast_%s_taxa_%s_sites_%d_stats.log"

# gt16
num_sites = 200
sites_200, ess_200 = get_ess_time_stats(gt16_time_log, gt16_ess_log, num_taxa=num_taxa, num_sites=num_sites)
num_sites = 500
sites_500, ess_500 = get_ess_time_stats(gt16_time_log, gt16_ess_log, num_taxa=num_taxa, num_sites=num_sites)

# gt16 error model
num_sites = 200
sites_200_em, ess_200_em = get_ess_time_stats(gt16_time_log_em, gt16_ess_log_em, num_taxa=num_taxa, num_sites=num_sites)
num_sites = 500
sites_500_em, ess_500_em = get_ess_time_stats(gt16_time_log_em, gt16_ess_log_em, num_taxa=num_taxa, num_sites=num_sites)

# calculate ess per hour
ratio_200 = get_ess_per_hour(sites_200, ess_200)
ratio_500 = get_ess_per_hour(sites_500, ess_500)
ratio_200_em = get_ess_per_hour(sites_200_em, ess_200_em)
ratio_500_em = get_ess_per_hour(sites_500_em, ess_500_em)

# font settings
SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 14

plt.rcParams['figure.figsize'] = (6, 4.5)
plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# plot ESS per hour
fig = plt.figure()
ax = plt.subplot(111)
plt.scatter(x=[0.4] * num_repeats, y=ratio_200, label="GT16", color="tab:cyan", alpha=0.8)
plt.scatter(x=[0.6] * num_repeats, y=ratio_200_em, label="GT16 EM", color="tab:red", alpha=0.8)
plt.scatter(x=[0.9] * num_repeats, y=ratio_500, color="tab:cyan", alpha=0.8)
plt.scatter(x=[1.1] * num_repeats, y=ratio_500_em, color="tab:red", alpha=0.8)
plt.scatter(x=0.4, y=np.mean(ratio_200), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=0.6, y=np.mean(ratio_200_em), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=0.9, y=np.mean(ratio_500), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=1.1, y=np.mean(ratio_500_em), marker='_', lw=1.5, color="black", alpha=1)
plt.xticks([0.5, 1], ["200", "500"])
plt.legend(title="Model")
plt.ylabel("ESS per hour")
plt.xlabel("Number of sites")
plt.title("ESS per hour")
# remove borders
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)
# legend pos
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(title="Model", loc='center left', bbox_to_anchor=(1.02, 0.5))
plt.savefig("../figures/gt16_ESS_per_hour_vs_sites.pdf")

# plot total runtime
fig = plt.figure()
ax = plt.subplot(111)
y1 = [x / SECONDS_PER_HOUR for x in sites_200]
y2 = [x / SECONDS_PER_HOUR for x in sites_200_em]
y3 = [x / SECONDS_PER_HOUR for x in sites_500]
y4 = [x / SECONDS_PER_HOUR for x in sites_500_em]
plt.scatter(x=[0.4] * num_repeats, y=y1, label='GT16', color="tab:cyan", alpha=0.8)
plt.scatter(x=[0.6] * num_repeats, y=y2, label='GT16 EM', color="tab:red", alpha=0.8)
plt.scatter(x=[0.9] * num_repeats, y=y3, color="tab:cyan", alpha=0.8)
plt.scatter(x=[1.1] * num_repeats, y=y4, color="tab:red", alpha=0.8)
plt.scatter(x=0.4, y=np.mean(y1), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=0.6, y=np.mean(y2), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=0.9, y=np.mean(y3), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=1.1, y=np.mean(y4), marker='_', lw=1.5, color="black", alpha=1)
plt.xticks([0.5, 1], ["200", "500"])
plt.legend(title="Model")
plt.ylabel("Hours")
plt.xlabel("Number of sites")
plt.title("Total runtime for 10 Mil samples")
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(title="Model", loc='center left', bbox_to_anchor=(1.02, 0.5))
plt.savefig("../figures/gt16_runtime_vs_sites.pdf")

# plot minimum ESS
fig = plt.figure()
ax = plt.subplot(111)
plt.scatter(x=[0.4] * num_repeats, y=ess_200, label='GT16', color="tab:cyan", alpha=0.8)
plt.scatter(x=[0.6] * num_repeats, y=ess_200_em, label='GT16 EM', color="tab:red", alpha=0.8)
plt.scatter(x=[0.9] * num_repeats, y=ess_500, color="tab:cyan", alpha=0.8)
plt.scatter(x=[1.1] * num_repeats, y=ess_500_em, color="tab:red", alpha=0.8)
plt.scatter(x=0.4, y=np.mean(ess_200), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=0.6, y=np.mean(ess_200_em), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=0.9, y=np.mean(ess_500), marker='_', lw=1.5, color="black", alpha=1)
plt.scatter(x=1.1, y=np.mean(ess_500_em), marker='_', lw=1.5, color="black", alpha=1)
plt.xticks([0.5, 1], ["200", "500"])
plt.ylabel("Minimum ESS")
plt.xlabel("Number of sites")
plt.title("Minimum ESS in 10 Mil samples")
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(title="Model", loc='center left', bbox_to_anchor=(1.02, 0.5))
plt.savefig("../figures/gt16_ESS_vs_sites.pdf")
