# -*- coding: utf-8 -*-

# Import packages
from core import Diagram
import argparse
import os
import networkx as nx
import pandas as pd

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotation", required=True, help="Path to the pandas "
                                                          "DataFrame with AI2D "
                                                          "annotation.")
ap.add_argument("-i", "--images", required=True, help="Path to the directory "
                                                      "with AI2D images.")
ap.add_argument("-o", "--output", required=True, help="Path to the output.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
images_path = args['images']
output_path = args['output']

# Check if the output file exists already, or whether to continue with previous
# annotation.
if os.path.isfile(output_path):

    # Read existing file
    annotation_df = pd.read_pickle(output_path)

# Otherwise, read the annotation from the input DataFrame
if not os.path.isfile(output_path):

    # Make a copy of the input DataFrame
    annotation_df = pd.read_pickle(ann_path).copy()

    # Set up an empty column to hold the diagram
    annotation_df['diagram'] = None

# Begin looping over the rows of the input DataFrame. Enumerate the result to
# show annotation progress to the user.
for i, (ix, row) in enumerate(annotation_df.iterrows(), start=1):

    # Begin the annotation by clearing the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Fetch the filename of current diagram image
    image_fname = row['image_name']

    # Join with path to image directory with current filename
    image_path = os.path.join(images_path, row['image_name'])

    # Print status
    print("Now processing row {}/{} ({}) ...".format(i, len(annotation_df),
                                                     image_fname))

    # Fetch the annotation dictionary from the DataFrame
    annotation = row['annotation']

    # Assign diagram to variable
    diagram = row['diagram']

    # Check if diagram exists by requesting input
    try:
        diagram.request_input()

    # If a non-existent diagram throws an error, create a new diagram
    except AttributeError:

        # Initialise a Diagram class and assign to variable
        diagram = Diagram(annotation, image_path)

        # Request user input
        diagram.request_input()

    # Store the diagram into the column 'diagram'
    annotation_df.at[ix, 'diagram'] = diagram

    # Write the DataFrame to disk at each step
    annotation_df.to_pickle(output_path)
