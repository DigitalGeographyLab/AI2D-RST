# -*- coding: utf-8 -*-

from core import Diagram
import argparse
import cv2
import numpy as np
import os
import pandas as pd

"""
This script visualises the Diagram objects that contain the descriptions of
diagram structure. The visualisation will show the graph representing the
logical structure and the layout annotation side by side.

Usage:
    python visualize_diagrams_in_df.py -a annotation.pkl -i images/ -c

Arguments:
    -a/--annotation: Path to the pandas DataFrame containing the annotation
                 extracted from the AI2D dataset.
    -i/--images: Path to the directory containing the AI2D diagram images.
    -c/--comments: Print out the comments stored during the annotation process.
    
Returns:
    None
"""

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotation", required=True)

ap.add_argument("-i", "--images", required=True,
                help="Path to directory with AI2D image files.")

ap.add_argument("-c", "--comments", action='store_true', dest='comments',
                help="Print comments about diagrams.")

# Parse arguments
args = vars(ap.parse_args())

# Assign required arguments to variables
ann_path = args['annotation']
img_path = args['images']

# Check optional arguments
if args['comments']:
    comments = args['comments']
else:
    comments = False

# Read the DataFrame
annotation_df = pd.read_pickle(ann_path)

# Begin looping over the rows of the input DataFrame. Enumerate the result to
# show annotation progress to the user.
for i, row in annotation_df.iterrows():

    # Fetch the filename of current diagram image
    image_fname = row['image_name']

    # Join with path to image directory with current filename
    image_path = os.path.join(img_path, row['image_name'])

    try:
        # Assign diagram to variable
        diagram = row['diagram']

        # Draw the graph
        layout_graph = diagram.draw_graph(dpi=100)

        # Join the graph and layout visualizations
        preview = np.hstack((layout_graph, diagram.layout))

        # Show the visualization
        cv2.imshow("{}".format(image_fname), preview)

        # If comments exist and have been requested, print the comments
        if comments:

            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')

            # Print each comment on separate row
            for d in diagram.comments:
                print(d)
        else:
            pass

        # If the user presses 'q', then exit, otherwise show next diagram.
        if cv2.waitKey() == ord('q'):
            quit()

        # Destroy all windows
        cv2.destroyAllWindows()

    # Otherwise, continue to next row
    except AttributeError:
        continue

