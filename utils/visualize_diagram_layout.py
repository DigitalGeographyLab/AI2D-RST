#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script visualizes information about diagram elements stored in the AI2D annotation,
namely the polygons and rectangles which mark the position of graphical elements, text
blocks and diagrammatic elements such as arrows and lines.

The script loops through directories containing the diagram images and their annotation,
displaying the original and the annotation side by side.

Usage:
    python visualize_diagram_layout.py -a annotation/ -i images/
    
Arguments:
    -a/--annotation: Path to directory containing the AI2D annotation files in JSON.
    -i/--images: Path to the directory containing the AI2D diagram images.

Returns:
    None
"""

# Import packages
import argparse
import cv2
import json
import numpy as np
import os

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotations", required=True)
ap.add_argument("-i", "--images", required=True)

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotations']
img_path = args['images']

# Walk through the directory containing the annotations
for (ann_root, ann_dirs, ann_files) in os.walk(ann_path):
    # Loop over the files
    for f in ann_files:
        # Process JSON files only
        if f.split('.')[-1] == 'json':
            # Retrieve the unique identifier from the filename (position -3) and
            # reconstruct the image file name.
            image_fn = f.split('.')[-3] + '.png'

            # Get paths to annotation and image
            json_path = os.path.join(ann_root, f)
            image_path = os.path.join(img_path, image_fn)

            # Load the AI2D annotation stored in the JSON file
            with open(json_path) as data_file:
                # Assign the annotation to variable 'ann'
                ann = json.load(data_file)

            # Read the diagram image file using OpenCV
            img = cv2.imread(image_path)

            # Create an empty image for vizualising the annotations and set
            # background colour to white (255) using the fill method. The shape
            # of this empty image matches that of the input file ('img.shape').
            viz = np.zeros(img.shape, np.uint8)
            viz.fill(255)

            # Begin by drawing blobs (i.e. polygons). First, we check if blobs
            # exist in the JSON annotation.
            if len(ann['blobs']) > 0:
                # Draw the polygon for each blob 'b' in the annotation
                for b in ann['blobs']:
                    # Assign the points into a variable and convert into a numpy
                    # array
                    points = np.array(ann['blobs'][b]['polygon'], np.int32)
                    # Reshape the numpy array for drawing
                    points = points.reshape((-1, 1, 2))
                    # Draw the polygon. Note that points must be in brackets to
                    # be drawn as lines; otherwise only points will appear.
                    cv2.polylines(viz, [points], isClosed=True,
                                  color=(0, 0, 255), thickness=1,
                                  lineType=cv2.LINE_AA)

            # Continue by drawing text boxes in the annotation
            if len(ann['text']) > 0:
                # Draw text blocks
                for t in ann['text']:
                    # Get the start and end points of the rectangle and cast
                    # them into tuples for drawing.
                    rect = ann['text'][t]['rectangle']
                    start, end = tuple(rect[0]), tuple(rect[1])
                    # Draw the rectangle
                    cv2.rectangle(viz, start, end, color=(255, 0, 0),
                                  thickness=1, lineType=cv2.LINE_AA)

            # Next, we draw any arrows in the annotation
            if len(ann['arrows']) > 0:
                # Draw arrows
                for a in ann['arrows']:
                    # Assign the points into a variable
                    points = np.array(ann['arrows'][a]['polygon'], np.int32)
                    # Reshape the numpy array for drawing
                    points = points.reshape((-1, 1, 2))
                    # Draw the polygon. Note that points must be in brackets to
                    # be drawn as lines; otherwise only points will appear.
                    cv2.polylines(viz, [points], isClosed=True,
                                  color=(0, 255, 0), thickness=1,
                                  lineType=cv2.LINE_AA)

            # Combine image and the visualization
            preview = np.concatenate([img, viz], axis=1)

            # Calculate aspect ratio (target width / current width) and new
            # width of the preview image
            ratio = 800.0 / preview.shape[1]
            size = (800, int(preview.shape[0] * ratio))
            # Resize the preview image
            preview = cv2.resize(preview, size, interpolation=cv2.INTER_AREA)

            # Show the visualization
            cv2.imshow("Preview", preview)
            # Print the filename for the diagram that's being shown
            print("Current diagram: {}".format(f))
            # If the user presses 'q', then exit, otherwise show next diagram.
            if cv2.waitKey() == ord('q'):
                quit()
