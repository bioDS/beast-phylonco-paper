#!/bin/bash
# Description: sequence simulation for a fixed tree
# Usage: ./run_simulation.sh
mkdir -p ../data/binary_beta
mkdir -p ../data/binary_alpha

echo "Simulating data"
Rscript "simulate_binary.r"
