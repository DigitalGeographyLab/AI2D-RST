#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script draws a random sample from a pandas DataFrame containing annotation
extracted from the AI2D dataset.

This sample is intended for evaluating agreement between annotators applying
Rhetorical Structure Theory to the sample. For this reason, the semantic
relation "arrowHeadTail" is dropped.

Usage:
    python extract_semantic_relations.py -a annotation.pkl -o output.pkl

Arguments:
    -a/--annotation: Path to the pandas DataFrame containing the annotation
                     extracted from the AI2D dataset.
    -p/--percentage: An integer indicating the percentage of the annotation to
                     include in the random sample.
    -o/--output: Path to the output file, which contains the sample taken from
                 the input file.

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
ap.add_argument("-p", "--percentage", required=True)
ap.add_argument("-o", "--output", required=True)

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
percent = args['percentage']
output_path = args['output']

# Read the annotation from the input DataFrame
annotation_df = pd.read_pickle(ann_path)

# Drop the semantic relations that are annotated as 'arrowHeadTail'.
annotation_df = annotation_df[annotation_df['category'] != 'arrowHeadTail']

# Calculate the number of sample
sample_n = int((len(annotation_df) / 100) * int(percent))

# Sample the annotation without replacement as requested
sample = annotation_df.sample(n=sample_n, replace=False, random_state=7)

# Print status message
print("[INFO] Randomly sampled the data for {} relations.".format(len(sample)))

# Save the sample to disk
sample.to_pickle(output_path)

# Print status to user
print("[INFO] Done. Saved the output to {}.".format(output_path))