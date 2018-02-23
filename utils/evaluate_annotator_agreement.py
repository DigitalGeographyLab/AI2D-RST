#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script loads AI2D annotations from different annotators and reports the
results for various measurements of inter-annotator agreement and reliability.

Usage:
    python evaluate_annotator_agreement.py -a1 ann_1.pkl -a2 ann_2.pkl

Arguments:
    -a1/--annotation_1: Path to the pandas DataFrame containing annotation for
                        annotator #1.
    -a2/--annotation_2: Path to the pandas DataFrame containing annotation for
                        annotator #2.

Returns:
    Prints the measurements for inter-annotator agreement on the standard output
    for rhetorical relations and nuclearity.
"""

# Import packages
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
from nltk.metrics import AnnotationTask
import argparse
import numpy as np
import pandas as pd


# Start by defining a function that compares the work of different annotators
def compare_annotation(list_one, list_two):
    """
    This function takes two lists of annotations, converts them into numerical
    form for comparison, and applies several measures of inter-annotator
    agreement implemented in NLTK, including average observed agreement, Scott's
    pi, Fleiss' kappa and Krippendorff's alpha.

    Parameters:
        list_one: A list containing the annotation by annotator 1.
        list_two: A list containing the annotation by annotator 2.

    Returns:
        A print providing the values for various measures of inter-annotator
        agreement.
    """

    # Use set() to retrieve unique values for both annotators
    unique_values = list(set(list_one + list_two))

    # Initialize scikit-learn LabelEncoder and encode labels for unique values
    le = LabelEncoder()  # initialize the encoder
    le.fit(unique_values)  # extract labels
    num_classes = le.transform(list(le.classes_))  # labels into numbers

    # Zip the unique annotations and their corresponding identifiers into a dict
    labeldict = dict(zip(le.classes_, num_classes))

    # Set up a dictionary to hold the annotations in numerical form
    annotation = {}

    # Encode numerical predictions for both annotators
    annotation['annotator_1'] = [labeldict[x] for x in list_one]
    annotation['annotator_2'] = [labeldict[x] for x in list_two]

    # Set up list for task data
    annotation_data = []

    # Construe input for NLTK's agreement module by looping over the frameworks
    for i, f in enumerate(annotation.keys(), start=1):
        # Loop over the predictions made by each framework
        for x in range(0, len(annotation[f])):
            # Construe the annotation tuple
            annotation_entry = (i, x, annotation[f][x])
            # Append the annotation tuple to the list
            annotation_data.append(annotation_entry)

    # Calculate agreement
    task = AnnotationTask(data=annotation_data)

    print("Number of available categories: {}".format(len(labeldict)))
    print("Average observed agreement: {:.4f}".format(task.avg_Ao()))
    print("Scott's pi: {:.4f}".format(task.pi()))
    print("Fleiss' kappa: {:.4f}".format(task.kappa()))
    print("Krippendorff's alpha: {:.4f}\n".format(task.alpha()))

    print(classification_report(annotation['annotator_1'],
                                annotation['annotator_2'],
                                target_names=le.classes_))


# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a1", "--annotation_1", required=True,
                help="Path to the pandas DataFrame containing annotation by "
                     "annotator 1.")
ap.add_argument("-a2", "--annotation_2", required=True,
                help="Path to the pandas DataFrame containing annotation by "
                     "annotator 2.")

# Parse arguments
args = vars(ap.parse_args())

# Load the annotations by each annotator from disk
annotator_1 = pd.read_pickle(args['annotation_1'])
annotator_2 = pd.read_pickle(args['annotation_2'])

# Fetch the annotation for RST relations from each annotator
rst_relations_1 = annotator_1['rst_relation'].tolist()
rst_relations_2 = annotator_2['rst_relation'].tolist()

# Check that the lists containing RST relations are of equal length
assert len(rst_relations_1) == len(rst_relations_2)

# Compare the annotation for RST relations
print("\nInter-annotator agreement for RST relations:\n")
compare_annotation(rst_relations_1, rst_relations_2)

# Fetch the annotation for nuclearity for each annotator
origin_1 = annotator_1['origin_role'].tolist()
origin_2 = annotator_2['origin_role'].tolist()
destination_1 = annotator_1['destination_role'].tolist()
destination_2 = annotator_2['destination_role'].tolist()

# Check that the lists for origin and destination roles are equally long
assert len(origin_1) == len(origin_2)
assert len(destination_1) == len(destination_1)

# Compare the annotation for origin role
print("\nInter-annotator agreement for origin role:\n")
compare_annotation(origin_1, origin_2)

# Compare the annotation for destination role
print("\nInter-annotator agreement for destination role:\n")
compare_annotation(destination_1, destination_2)
