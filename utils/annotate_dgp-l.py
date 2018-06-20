# -*- coding: utf-8 -*-

"""
This script allows the user to create a graph describing the logical structure
of a diagram (DPG-L).

Usage:
    python annotate_dpg-l.py -a annotation.pkl -i images/ -o output.pkl
    
Arguments:
    -a/--annotation: Path to the pandas DataFrame containing the annotation
                     extracted from the AI2D dataset.
    -i/--images: Path to the directory containing the AI2D diagram images.
    -o/--output: Path to the output file, in which the resulting annotation is
                 stored.
    -r/--review: Optional argument that activates review mode. This mode opens
                 each Diagram object marked as complete for editing.

Returns:
    A pandas DataFrame containing a Diagram object for each diagram.
"""

# Import packages
from core import Diagram
import argparse
import os
import pandas as pd

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotation", required=True,
                help="Path to the pandas DataFrame with AI2D annotation.")
ap.add_argument("-i", "--images", required=True,
                help="Path to the directory with AI2D images.")
ap.add_argument("-o", "--output", required=True,
                help="Path to the file in which the annotation is stored.")
ap.add_argument("-r", "--review", required=False, action='store_true',
                help="Activates review mode, which opens each annotated diagram"
                     " for inspection.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
images_path = args['images']
output_path = args['output']

# Set review / annotation mode
if args['review']:
    review = True
else:
    review = False

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

    # If diagram is marked as complete, but the script runs in a review mode,
    # open the diagram for editing.
    if diagram.complete and review:

        # Set the method tracking completeness to False
        diagram.complete = False

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
