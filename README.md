# Phylonco analysis

This repository contains data and analysis scripts that accompany the Beast Phylonco paper below.

[Paper](https://doi.org/10.1101/2021.03.17.435906): Chen et al. "Accounting for errors in data improves timing in single-cell cancer evolution." (2022)

[Beast Phylonco Software](https://www.github.com/bioDS/beast-phylonco): A BEAST2 package for single-cell phylogenetic analysis of cancer evolution.

## Software requirements
Java 8 and [BEAST v2.5](https://github.com/CompEvol/beast2) 

We provide a bundled jar version of BEAST2.5 with Phylonco in `beast-phylonco.jar`, also see [analysis section](https://github.com/bioDS/beast-phylonco-paper/edit/main/README.md#running-the-analysis).

Python 3 and packages: 
```
DendroPy~=4.5.2
lxml~=4.8.0
matplotlib~=3.4.3
numpy~=1.21.2
seaborn~=0.11.2
```

R language, [tracerR](https://github.com/walterxie/TraceR) and packages: 
```
ape
expm
ggtree
ggplot2
tools
treeio
TreeSimGM
```

(Optional) Simulating new GT16 datasets additionally requires Java 16, [LPhy](https://github.com/LinguaPhylo/linguaPhylo) and [LPhyBeast](https://github.com/LinguaPhylo/LPhyBeast). 

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

Go to the `sim1/scripts` or `sim2/scripts` sub-directory

Run `simulate_binary.sh`

Run `python3 binary_xml_transformer.py`

**GT16 datasets:**

Run LPhyBeast with arguments `-l <chain length> -r <num repeats> <path to lphy script>`

* chain length: length of the mcmc chain

* num repeats: number of experimental repeats, e.g. `-r 10` for 10 repeats

* path to lphy script: lphy scripts are in `sim3/scripts/*.lphy` and `sim7/scripts/*.lphy`

Example command:

`LPhyBeast -l 10000000 -r 10 sim7/scripts/gt16_delta_0.lphy`

## Running the analysis
**Running BEAST2:**

We provide a bundled jar version of BEAST2 with Phylonco and related packages. This does not require a separate BEAST2 install.

To run the analysis, use `java -jar beast-phylonco.jar <path to xml>`.

Substitute `<path to xml>` with the file path to the Beast XML file. 

Example command:

`java -jar beast-phylonco.jar sim1/data/binary_yule_n30_L400_0.xml`

**Post-processing:**

Beast log stats: from R run `scripts/mcmc_stats.r` (edit "mcmc_path" to point to your beast logs directory).

Beast log viewer: logs can be viewed using Tracer.

Beast tree stats: trees can be summarized using `TreeAnnotator` that is bundled with Beast software.

Beast tree viewer: trees can be viewed using Figtree or any compatible beast tree visualization software.

## Visualizing output 
Coverage plots: run `python3 plot_coverage.py` from the `scripts` sub-directory.

Tree statistics plots: run `python3 plot_tree_stats.py` from the `scripts` sub-directory.

Summary tree plots: run `plot_tree_*.py` from the `scripts` sub-directory.

Extra supplementary plots: run `python3 plot_*.py` from the `scripts` sub-directory.

