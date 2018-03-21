#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import packages
from core_functions import Annotate, Draw
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
    annotation_df = pd.read_pickle(output_path)

# Otherwise, read the annotation from the input DataFrame
if not os.path.isfile(output_path):
    annotation_df = pd.read_pickle(ann_path).copy()

# Set up an empty column for graphs
annotation_df['grouped_graph'] = None

# Begin looping over the rows of the input DataFrame. Enumerate the result to
# show annotation progress to the user.
for i, (ix, row) in enumerate(annotation_df.iterrows(), start=1):

    # Begin the annotation by clearing the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Fetch the filename of current diagram image
    image_fname = row['image_name']

    # Print status
    print("Now processing row {}/{} ({}) ...".format(i, len(annotation_df),
                                                     image_fname))

    # Join with path to image directory with current filename
    image_path = os.path.join(images_path, row['image_name'])

    # Fetch the annotation dictionary from the DataFrame
    annotation = row['annotation']

    # Draw the diagram and graph based on the annotation
    diagram, graph = Draw.draw_graph_from_annotation(annotation,
                                                     draw_edges=False,
                                                     draw_arrowheads=False,
                                                     return_graph=True)

    # Visualise the diagram layout based on the annotation
    layout = Draw.draw_layout(image_path, annotation)

    # Annotate the diagram for element groups
    output = Annotate.request_input(graph, layout)

    # Check the object returned by the request_input function
    if output is not None:

        # If the output is a string, assume a comment
        if isinstance(output, str):

            # Store comment into the 'comment' column
            annotation_df.at[ix, 'comment'] = output

            # Re-enter the annotation procedure
            output = Annotate.request_input(graph, layout)

        # If the output is a graph, assume annotation is complete
        if isinstance(output, nx.Graph):

            # Store the graph into the 'grouped_graph' column
            annotation_df.at[ix, 'grouped_graph'] = output

            # Write the DataFrame to disk
            annotation_df.to_pickle(output_path)
