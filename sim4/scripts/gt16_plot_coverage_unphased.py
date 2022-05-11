import matplotlib.pyplot as plt

lphy_to_beast = {
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
    "rates.AC": "rate AC",
    "rates.AG": "rate AG",
    "rates.AT": "rate AT",
    "rates.CG": "rate CG",
    "rates.CT": "rate CT",
    "rates.GT": "rate GT",
    "Theta": r"$\theta$",
    "delta": r"$\delta$",
    "epsilon": r"$\epsilon$"
}

lphy_to_beast_len = len(lphy_to_beast)


def do_work(fileid):
    stats_file = "../stats/gt16CoalUnphasedErrModel_%s_stats.log" % fileid
    true_file = "../data/gt16CoalErrModel_%s_true.log" % fileid

    mean = []
    hdp95lower = []
    hdp95upper = []
    ess = []

    # Read Stat Record
    try:
        handle = open(stats_file)
        for line in handle:
            line = line.strip()
            if line.startswith('mean'):
                eles = line.split('\t')
                mean = eles[4: 4 + lphy_to_beast_len]

            elif line.startswith('HPD95.lower'):
                eles = line.split('\t')
                hdp95lower = eles[4: 4 + lphy_to_beast_len]

            elif line.startswith('HPD95.upper'):
                eles = line.split('\t')
                hdp95upper = eles[4: 4 + lphy_to_beast_len]

            elif line.startswith('ESS'):
                eles = line.split('\t')
                ess = eles[4: 4 + lphy_to_beast_len]

        handle.close()

        # Read true record
        handle = open(true_file)
        handle.readline()
        line = handle.readline().strip()
        true_record = line.split('\t')[1:]

        # Merge them
        merge = []
        for i in range(lphy_to_beast_len):
            merge.append((true_record[i], mean[i], hdp95upper[i], hdp95lower[i], ess[i]))

        return merge
    except FileNotFoundError:
        print("missing file id: %s" % fileid)
        return None


def plot_hpd():
    total_files = 0
    items = []
    for i in range(100):
        data = do_work(i)
        if data is not None:
            items.append(data)
            total_files += 1

    # Let's plot
    keys = list(lphy_to_beast)
    # for i in range(lphy_to_beast_len):
    print("param\tminESS\tmean HPD\tcoverage")

    # p = (0, 1)

    pairs = [(1, 4), (2, 8), (3, 12), (6, 9), (7, 13), (11, 14)]
    paired = True
    for p in pairs:

    # paired = False
    # for i in range(lphy_to_beast_len):
        if paired:
            i = p[0]
            j = p[1]
            param2 = keys[j]

        param = keys[i]

        # print("Going to plot line for %s " % (param))
        trues = []
        means = []
        uppers = []
        lowers = []
        esses = []
        colors = []

        for item in items:
            true = float(item[i][0])
            mean = float(item[i][1])
            upper = float(item[i][2])
            lower = float(item[i][3])
            ess = float(item[i][4])

            if paired:
                true += float(item[j][0])
                mean += float(item[j][1])
                upper += float(item[j][2])
                lower += float(item[j][3])
                ess += float(item[j][4])

            trues.append(true)
            means.append(mean)
            uppers.append(upper)
            lowers.append(lower)
            esses.append(ess)

            if lower <= true <= upper:
                colors.append('c')
            else:
                colors.append('r')

        plt.rcParams["figure.figsize"] = (3.5, 3)

        a = min(trues)
        b = max(trues)

        xaxis = trues  # trues

        # print coverage and ESS
        hpd_range = [uppers[x] - lowers[x] for x in range(total_files)]
        mean_hpd = sum(hpd_range) / total_files
        coverage = 100 * colors.count("c") / (total_files + 0.0)
        print("%s & %.2f & %.2f & %.0f" % (lphy_to_beast[param], min(esses), mean_hpd, coverage) + "\\% \\\\")
        # print("%s\t%.2f\t%.2f\t%.0f" % (param, min(esses), mean_hpd, coverage) + "%")
        # print(esses.index(min(esses)))

        plt.plot([a, b], [a, b], 'k-', lw=0.5, label="x = y", zorder=10)
        plt.plot(xaxis, means, 'k.', ms=2, zorder=2)
        plt.vlines(xaxis, ymin=lowers, ymax=uppers, color=colors, alpha=0.5, lw=1, zorder=1)
        if param == "Theta":
            # plt.xscale("log")
            # plt.yscale("log")
            # plt.xlabel("true " + lphy_to_beast[param] + " (log scale)")
            # plt.ylabel("estimated " + lphy_to_beast[param] + " (log scale)")
            plt.xlabel("true " + lphy_to_beast[param])
            plt.ylabel("estimated " + lphy_to_beast[param])
            plt.title(lphy_to_beast[param])
            plt.tight_layout()
            # plt.savefig("unphase_err_" + param.replace(".", "_") + ".pdf", )
        else:
            if paired:
                plt.xlabel("true " + lphy_to_beast[param] + " + " + lphy_to_beast[param2])
                plt.ylabel("estimated " + lphy_to_beast[param] + " + " + lphy_to_beast[param2])
                plt.title(lphy_to_beast[param] + " + " + lphy_to_beast[param2])
                plt.tight_layout()
                # plt.savefig("unphase_err_sum_" + param.replace(".", "_") + ".pdf", )
            else:
                plt.xlabel("true " + lphy_to_beast[param])
                plt.ylabel("estimated " + lphy_to_beast[param])
                plt.title(lphy_to_beast[param])
                plt.tight_layout()
                # plt.savefig("unphase_err_" + param.replace(".", "_") + ".pdf", )

        plt.show()
        plt.clf()


plot_hpd()
