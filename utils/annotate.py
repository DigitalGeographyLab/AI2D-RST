# -*- coding: utf-8 -*-

"""
This script allows the user to annotate a diagram.

Usage:
    python annotate.py -a annotation.pkl -i images/ -o output.pkl
    
Arguments:
    -a/--annotation: Path to a pandas DataFrame with the original annotation
                     extracted from the AI2D dataset.
    -i/--images: Path to the directory with the AI2D diagram images.
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
                help="Activates review mode, which opens each diagram marked as"
                     " complete for inspection.")
ap.add_argument("-dr", "--disable_rst", required=False, action='store_true',
                help="Disables RST annotation.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
images_path = args['images']
output_path = args['output']

# Set review mode initially to false
review = False

# Activate review mode if requested using the -r/--review flag
if args['review']:

    review = True

if not args['review']:

    review = False

# Disable RST annotation if requested using the -dr/--disable_rst flag
if args['disable_rst']:

    disable_rst = True

if not args['disable_rst']:

    disable_rst = False

# Check if the output file exists already, or whether to continue with previous
# annotation.
if os.path.isfile(output_path):

    # Read existing file
    annotation_df = pd.read_pickle(output_path)

    # Print status message
    print("[INFO] Continuing with existing annotation in {}.".format(
        output_path))

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

    # Print status message
    print("[INFO] Now processing row {}/{} ({}) ...".format(i,
                                                            len(annotation_df),
                                                            image_fname))

    # Fetch the annotation dictionary from the DataFrame
    annotation = row['annotation']

    # Assign diagram to variable
    diagram = row['diagram']

    # Check if a Diagram object has been initialized
    if diagram is not None:

        # If the annotator runs in a review open the diagram for revision and
        # editing.
        if review:

            # Set the methods tracking completeness to False
            diagram.group_complete = False
            diagram.connectivity_complete = False
            diagram.rst_complete = False
            diagram.complete = False

    # If a Diagram object has not been initialized, create new
    elif diagram is None:

        # Initialise a Diagram class and assign to variable
        diagram = Diagram(annotation, image_path)

    # If the diagram has not been marked as complete, annotate
    if not diagram.complete:

        # Request the user to perform grouping (hierarchy + macro grouping)
        if not diagram.group_complete:

            # Annotate layout
            diagram.annotate_layout(review)

        # When initial grouping is done, move to annotate connectivity
        if diagram.group_complete:

            # Store the diagram into the column 'diagram'
            annotation_df.at[ix, 'diagram'] = diagram

            # Annotate connectivity
            diagram.annotate_connectivity(review)

        # When connectivity has been annotated, move to rhetorical structure
        if diagram.connectivity_complete and not disable_rst:

            # Store the diagram into the column 'diagram'
            annotation_df.at[ix, 'diagram'] = diagram

            # Annotate rhetorical structure
            diagram.annotate_rst(review)

            # Store the diagram into the column 'diagram'
            annotation_df.at[ix, 'diagram'] = diagram

        if diagram.group_complete and diagram.connectivity_complete \
                and diagram.rst_complete:

            # Mark diagram as complete
            diagram.complete = True

        # Otherwise, mark diagram as incomplete
        else:

            diagram.complete = False

    # Store the diagram into the column 'diagram'
    annotation_df.at[ix, 'diagram'] = diagram

    # Write the DataFrame to disk at each step
    annotation_df.to_pickle(output_path)
