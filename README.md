# Phylonco analysis

This repository contains data and analysis scripts for Beast Phylonco https://www.github.com/bioDS/beast-phylonco 

[Paper](https://doi.org/10.1101/2021.03.17.435906): Chen et al. "Accounting for errors in data improves timing in single-cell cancer evolution." (2022)


## Requirements
Java 8 and BEAST v2.5 or greater 

Python 3 and packages: 
```
matplotlib~=3.4.3
numpy~=1.21.2
seaborn~=0.11.2
pandas~=1.3.5
scipy~=1.7.3
ete3~=3.1.2
DendroPy~=4.5.2
```

R language, [tracerR](https://github.com/walterxie/TraceR) and packages: 
```
expm
ape
TreeSimGM
ggtree
treeio
ggplot2
```

(Optional) Simulating new GT16 datasets additionally requires Java 16, LPhy and LPhyBeast. 

## Datasets
**Simulated datasets:**

Simulated datasets and parameters are in the directories `sim1/data` to `sim7/data`. 

True simulation parameters are stored in the files `*_true.csv` or `*_true.log` and true trees are stored in the files `*._true.trees`. 

Beast analysis XML files are in sub-directories `sim1/beast` to `sim7/beast` for each dataset.

**Real datasets:**

Real datasets are available in FASTA format (with GT16 encoding) in `E15/data` and `L86/data`.

Beast analysis XML files are in `E15/data/*.xml` and `L86/data/*.xml`

## Simulating new datasets

**Binary datasets:**

Go to the `sim1/scripts` or `sim2/scripts` sub-directory, run `simulate_binary.sh`, then run `python3 binary_xml_transformer.py`.

**GT16 datasets:**

Run LPhyBeast with arguments `-l <chain length> -r <num repeats> <path to lphy script>`

Example command:

`LPhyBeast -l 10000000 -r 10 sim7/scripts/gt16_delta_0.lphy`

* chain length: length of the mcmc chain

* num repeats: number of experimental repeats, e.g. `-r 10` for 10 repeats

* path to lphy script: lphy scripts are in `sim3/scripts/*.lphy` and `sim7/scripts/*.lphy`

## Running the analysis
**Running BEAST2:**

To run the analysis, go to the `scripts` sub-directory then use `java -jar beast-phylonco.jar <path to xml>`.

Substitute `<path to xml>` with the file path to the Beast XML file. 

**Post-processing:**

Beast log stats: from R run `scripts/mcmc_stats.r` (you may need to edit "mcmc_path" to the directory with your beast logs).

Beast log viewer: logs can be viewed using Tracer.

Beast tree stats: trees can be summarized using `TreeAnnotator` that is bundled with Beast software.

Beast tree viewer: trees can be viewed using Figtree or any compatible beast tree software.

## Visualizing output 
Coverage plots: run `python3 plot_coverage.py` from the `scripts` sub-directory.

Tree statistics plots: run `python3 plot_tree_stats.py` from the `scripts` sub-directory.

Extra supplementary plots: run `python3 plot_*.py` from the `scripts` sub-directory.

