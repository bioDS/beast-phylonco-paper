#!/bin/bash
# Description: simulate binary sequences from Yule trees
# Usage: ./run_simulation.sh
mkdir -p output/sequences
mkdir -p output/xml
mkdir -p output/beast

cd r

echo "Simulating data"
Rscript "simulate_tree_error_large_binary.r"
