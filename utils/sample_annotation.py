#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script draws a random sample from a pandas DataFrame containing annotation
extracted from the AI2D dataset.

Usage:
    To randomly sample 20 diagrams from the AI2D dataset:
    
    python extract_semantic_relations.py -a annotation.pkl -o output.pkl -n 20

    To randomly sample 1% of the diagrams in the AI2D dataset:
    
    python extract_semantic_relations.py -a annotation.pkl -o output.pkl -p 0.01

Arguments:
    -a/--annotation: Path to the pandas DataFrame containing the annotation
                     extracted from the AI2D dataset.
    -p/--percentage: An integer indicating the percentage of the annotation to
                     include in the random sample.
    -n/--number: Number of diagrams to include in the random sample.
    -o/--output: Path to the output file, in which to store the sample taken 
                from the input file.

Returns:
    A pandas DataFrame containing the sample drawn from the AI2D annotation.
"""

# Import packages
import argparse
import pandas as pd

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotation", required=True)
ap.add_argument("-p", "--percentage", required=False)
ap.add_argument("-n", "--number", required=False)
ap.add_argument("-o", "--output", required=True)

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
output_path = args['output']
percent = args['percentage']
number = args['number']

# Read the annotation from the input DataFrame
annotation_df = pd.read_pickle(ann_path)

# If a percentage is requested, calculate the number of diagrams to retrieve
if percent:
    sample_n = int((len(annotation_df) / 100) * int(percent))

# If a certain number is requested, use this number
if number:
    sample_n = int(number)

# Sample the annotation without replacement as requested
sample = annotation_df.sample(n=sample_n, replace=False, random_state=11)

# Print status message
print("[INFO] Randomly sampled the data for {} diagrams.".format(len(sample)))

# Save the sample to disk
sample.to_pickle(output_path)

# Print status to user
print("[INFO] Done. Saved the output to {}.".format(output_path))
