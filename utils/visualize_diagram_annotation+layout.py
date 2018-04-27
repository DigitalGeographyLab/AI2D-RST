#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core import Diagram
import argparse
import cv2
import numpy as np
import os

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotation", required=True, help="Path to directory"
                                                          "with AI2D "
                                                          "annotation files.")
ap.add_argument("-i", "--images", required=True, help="Path to directory with "
                                                      "AI2D image files.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
img_path = args['images']

# Check the type of input, beginning with files
if os.path.isfile(ann_path) and os.path.isfile(img_path):

    # Initialise diagram
    diagram = Diagram(ann_path, img_path)

    # Create a diagram with original annotation
    diagram.graph = diagram.create_graph(diagram.annotation,
                                         edges=True, arrowheads=True)

    # Visualize the graph
    graph_viz = diagram.draw_graph(dpi=100)

    # Join the graph and layout visualizations
    preview = np.hstack((graph_viz, diagram.layout))

    # Show the visualization
    cv2.imshow("{}".format(img_path.split('/')[-1]), preview)

    # If the user presses 'q', then exit, otherwise show next diagram.
    if cv2.waitKey() == ord('q'):
        quit()

    # Destroy all windows
    cv2.destroyAllWindows()

# If the input is a dir ...
if os.path.isdir(ann_path) and os.path.isdir(img_path):

    # Walk through the directory containing the annotations
    for (ann_root, ann_dirs, ann_files) in os.walk(ann_path):

        # Loop over the files
        for f in ann_files:

            # Process JSON files only
            if f.split('.')[-1] == 'json':

                # Retrieve the unique identifier from the filename (position -3)
                # and reconstruct the image file name.
                image_fn = f.split('.')[-3] + '.png'

                # Get paths to annotation and image
                json_path = os.path.join(ann_root, f)
                image_path = os.path.join(img_path, image_fn)

                # Initialise diagram
                diagram = Diagram(json_path, image_path)

                # Create a diagram with original annotation
                diagram.graph = diagram.create_graph(diagram.annotation,
                                                     edges=True,
                                                     arrowheads=True)

                # Visualize the graph
                graph_viz = diagram.draw_graph(dpi=100)

                # Join the graph and layout visualizations
                preview = np.hstack((graph_viz, diagram.layout))

                # Show the visualization
                cv2.imshow("{}".format(image_fn), preview)

                # If user presses 'q', then exit, otherwise show next diagram
                if cv2.waitKey() == ord('q'):
                    quit()

                # Destroy all windows
                cv2.destroyAllWindows()