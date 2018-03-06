#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core_functions import Annotate, Draw
import argparse
import cv2
import json
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
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

# Load the annotation
ann = Annotate.load_annotation(ann_path)

# Draw the graph
diagram = Draw.draw_graph(ann)

# Draw the layout
layout = Draw.draw_layout(img_path, ann)

# Join the two images horizontally
preview = np.hstack((diagram, layout))

# Show the visualization
cv2.imshow("Preview", preview)

# If the user presses 'q', then exit, otherwise show next diagram.
if cv2.waitKey() == ord('q'):
    quit()

