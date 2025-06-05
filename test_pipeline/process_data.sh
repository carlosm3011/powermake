#!/bin/bash
# Simple script to process CSV data
echo "Processing data from: $1"
echo "--- Data Summary ---"
wc -l "$1"
echo "--- First 3 lines ---"
head -n 3 "$1"
echo "--- Cities ---"
cut -d',' -f3 "$1" | tail -n +2 | sort | uniq