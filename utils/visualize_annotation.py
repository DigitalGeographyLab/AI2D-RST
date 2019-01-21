# -*- coding: utf-8 -*-

"""
This script allows visualising AI2D-RST annotation stored in a pandas DataFrame.

Usage:
    python visualize_annotation.py -a annotation.pkl -i images/

Arguments:
    -a/--annotation: Path to the pandas DataFrame containing annotation.
    -i/--images: Path to the directory containing the original AI2D images.

Returns:
    Visualises the annotation for all layers and prints rhetorical relations,
    macro-groups and comments to standard output.
"""

# Import packages
from core.draw import *
from core.parse import *
from pathlib import Path
import argparse
import cv2
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import pandas as pd


# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotation", required=True,
                help="Path to the pandas DataFrame with AI2D-RST annotation.")
ap.add_argument("-i", "--images", required=True,
                help="Path to the directory with AI2D images.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
images_path = args['images']

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
images_path = args['images']

# Verify the input paths, print error and exit if not found
if not Path(ann_path).exists():

    exit("[ERROR] Cannot find {}. Check the input to -a!".format(ann_path))

if not Path(images_path).exists():

    exit("[ERROR] Cannot find {}. Check the input to -i!".format(images_path))

# Open the input file
annotation_df = pd.read_pickle(ann_path)

# Begin looping over the rows of the input DataFrame. Enumerate the result to
# show annotation progress to the user.
for i, (ix, row) in enumerate(annotation_df.iterrows(), start=1):

    # Fetch the filename of current diagram image
    image_fname = row['image_name']

    # Join with path to image directory with current filename
    image_path = os.path.join(images_path, row['image_name'])

    # Print status message
    print("[INFO] Now processing row {}/{} ({}) ...".format(i,
                                                            len(annotation_df),
                                                            image_fname))

    # Assign diagram to variable
    diagram = row['diagram']

    # Check if a Diagram object exists
    if diagram is not None:

        # Visualize the layout segmentation
        segmentation = draw_layout(diagram.image_filename,
                                   diagram.annotation,
                                   height=720,
                                   dpi=100)

        # Visualize grouping annotation
        grouping = draw_graph(diagram.layout_graph, dpi=100, mode='layout')

        # Visualize connectivity annotation
        connectivity = draw_graph(diagram.connectivity_graph, dpi=100,
                                  mode='connectivity')

        # Visualize RST annotation
        rst = draw_graph(diagram.rst_graph, dpi=100, mode='rst')

        # Stack segmentation and grouping annotation side by side
        seg_group = np.hstack([segmentation, grouping])

        # Stack connectivity and RST annotation side by side
        rst_group = np.hstack([connectivity, rst])

        # Stack the visualizations on top of each other
        whole_viz = np.vstack([seg_group, rst_group])

        # Generate a dictionary of RST relations present in the graph
        relation_ix = get_node_dict(diagram.rst_graph, kind='relation')

        # Loop through current RST relations and rename for convenience.
        relation_ix = {"R{}".format(i): k for i, (k, v) in
                       enumerate(relation_ix.items(), start=1)}

        # If more than one RST relation has been defined, print relations
        if len(relation_ix) > 0:

            # Print header for current RST relations
            print("\nCurrent RST relations \n---")

            # Print relations currently defined in the graph
            for k, v in relation_ix.items():

                print("{}: {}".format(k,
                                      diagram.rst_graph.nodes[v]['rel_name']))

            # Print closing line
            print("---")

        # Get current macro-groups from the layout graph
        macro_groups = dict(nx.get_node_attributes(diagram.layout_graph,
                                                   'macro_group'))

        # If more than one macro-group has been defined, print groups
        if len(macro_groups) > 0:

            # Print header for current macro-groups
            print("\nCurrent macro-groups \n---")

            # Print the currently defined macro-groups
            for k, v in macro_groups.items():
                print("{}: {}".format(k, v))

            # Print closing line
            print("---\n")

        # If comments have been provided, print them out
        if len(diagram.comments) > 0:

            # Print header for comments
            print("\nCurrent comments \n---")

            # Print each comment and a linebreak
            [print('#' + str(ic), comment) for ic, comment in enumerate(
                diagram.comments, start=1)]

            # Print final linebreak
            print("---\n")

        # Print instructions
        print("Print any key to continue or 'q' to exit.\n")

        # Show the visualization and print RST relations
        cv2.imshow("{} / {}".format(ann_path, image_fname), whole_viz)

        # Wait, quit if q is pressed
        if cv2.waitKey(0) == ord('q'):

            exit()

        # Destroy window
        cv2.destroyAllWindows()

        # Close any open plots
        plt.close()

print("[INFO] Done!")
