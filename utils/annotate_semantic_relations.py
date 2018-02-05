#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script loads information about semantic relations defined in the AI2D
dataset from a pandas DataFrame, in order to annotate them using Rhetorical
Structure Theory.

To continue annotation from a previous session, give the path to the existing
DataFrame to the -o/--output argument.

Usage:
    python annotate_semantic_relations.py -a annotation.pkl -o output.pkl

Arguments:
    -a/--annotation: Path to the pandas DataFrame containing the annotation
                 extracted from the AI2D dataset.
    -i/--images: Path to the directory containing the AI2D diagram images.
    -o/--output: Path to the output file, in which the resulting annotation is
                 stored.

Returns:
    A pandas DataFrame containing the annotation stored in the input DataFrame
    and the annotation created using this script.
"""

# Import packages
import argparse
import numpy as np
import os
import pandas as pd
import cv2


# Start by defining a convenience function for drawing annotation on images.
def draw(image, element_type, coords, role):
    """
    A function for visualizing the AI2D annotation on the diagram image.

    Parameters:
        image: The diagram image to draw on.
        element_type: A string indicating the type of element being drawn.
                      Either 'blob', 'arrow' or 'text'.
        coords: A list of coordinates indicating the location of the element.
        role: A string indicating the function of the element, either 'origin'
              or 'destination', depending on whether the relation originates or
              terminates at the element.

    Returns:
        Draws the annotation on the diagram image.
    """
    # Begin by checking for whether the element to be drawn stands for the
    # origin or the destination. This defines the colour used for drawing.
    if role == 'origin':
        color = (0, 0, 255)  # red
    if role == 'destination':
        color = (0, 255, 0)  # green

    # Next, check the type of the element that is being drawn. Begin with blobs
    # and arrows, which require drawing polygons.
    if element_type in ['blob', 'arrow']:

        # Convert the list into a NumPy array and reshape for drawing in OpenCV.
        origin_points = np.array(coords, np.int32)
        origin_points = origin_points.reshape(-1, 1, 2)

        # Draw the polygon
        cv2.polylines(image, [origin_points], isClosed=True, color=color,
                      thickness=2, lineType=cv2.LINE_AA)

    # Then check for rectangles, which are typically used for text boxes.
    if element_type == 'text':

        # Get the rectangle for the text block and extract the coordinates for
        # the start and end points.
        rectangle = coords
        start, end = tuple(rectangle[0]), tuple(rectangle[1])

        # Draw the rectangle
        cv2.rectangle(image, start, end, color=color, thickness=2,
                      lineType=cv2.LINE_AA)

    # Finally, check for the so-called image constants in the AI2D annotation,
    # which refer to the entire image.
    if element_type == 'entire_image':

        # Get the input image shape
        (height, width) = image.shape[:2]

        # Define a rectangle around the entire image. Note that width and height
        # need to be shifted around, because cv2.rectangle requires this order.
        # Use a 5 pixel buffer throughout.
        start, end = (5, 5), (width-5, height-5)

        # Draw the rectangle
        cv2.rectangle(image, start, end, color=color, thickness=2,
                      lineType=cv2.LINE_AA)


def print_info(question, request):
    """
    A function that prints provides additional commands and information during
    the annotation.

    Parameters:
        question: A string containing a standard question defined in the
                  annotation. The question must be one of the following:
                  rel_q (RST relation), nuclearity of origin (origin_q)
                  or nuclearity of destination (dest_q).
        request: A string indicating the requested information. Valid values
                 include 'info' for information and 'rels' for a list of RST
                 relations.

    Returns:
        A string containing the user's answer to the standard question.
    """
    # Print the requested information to the user
    if request == 'info':
        print(info)
    if request == 'rels':
        print(rels)
    # Use input to wait until the user is ready to continue
    input("Press Enter to continue ...")
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    # Present the requested standard question
    answer = input(question)
    # Return the answer
    return answer


# Define a string providing additional
info = """
       Available commands include:

       rels: Print a list of RST relations and their descriptions.
       quit: Exit without saving.
       """

# Define a string containing information on relations defined by Rhetorical
# Structure Theory.
rels = """Common RST relations for describing diagrams include:
        
        identification: A short text segment, such as a single noun or a noun 
                        group, which identifies an entity or its part(s). A 
                        common example would be a label for a part of an entity.
        elaboration:    A more extensive verbal description, such as a clause, 
                        which provides more specific information about some 
                        entity or its part(s).
        effect:         A generic mononuclear relation for describing processes 
                        that take place between entities, which are often 
                        reinforced using lines or arrows. The affected entity 
                        acts as the nucleus, while the origin of the effect acts
                        as the satellite.
        restatement:    A multinuclear relation holding between two entities 
                        that could act as a substitute for each other, such as 
                        the name of an entity and its visualisation.
        sequence:       A multinuclear relation indicating a temporal or spatial 
                        sequence holding between entities.
        title:          A text segment acting as the title for the entire 
                        diagram or its parts.
        
        """

# Define a dictionary of RST relations.
rel_dict = {'antithesis', 'background', 'circumstance', 'concession',
            'condition', 'elaboration', 'enablement', 'evaluation',
            'evidence', 'interpretation', 'justify', 'means', 'motivation',
            'nonvolitional-cause', 'nonvolitional-result', 'otherwise',
            'preparation', 'purpose', 'restatement', 'solutionhood',
            'summary', 'unless', 'volitional-cause', 'volitional-result',
            'contrast', 'joint', 'list', 'restatement', 'sequence',
            'identification', 'class-ascription', 'property-ascription',
            'possession', 'projection', 'effect', 'title', 'none'}

# Define a dictionary of roles for diagram elements
nuc_dict = {'n', 'nuc', 'nucleus', 's', 'sat', 'satellite'}

# Define standard questions presented to the user
rel_q = "Which rhetorical relation best describes the relation between " \
        "the source element (red) and the target element (green)? "
origin_q = "Does the origin element (red) act as a nucleus or a satellite? "
dest_q = "Does the destination element (green) act as a nucleus or a " \
           "satellite? "

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotation", required=True)
ap.add_argument("-i", "--images", required=True)
ap.add_argument("-o", "--output", required=True)

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
images_path = args['images']
output_path = args['output']

# Check if the output file exist already, or whether to continue with previous
# annotation.
if os.path.isfile(output_path):
    annotation_df = pd.read_pickle(output_path)

# Otherwise, read the annotation from the input DataFrame and create new columns
if not os.path.isfile(output_path):
    annotation_df = pd.read_pickle(ann_path)

    # Create a new column to hold the RST annotation and nuclearity information
    annotation_df['rst_relation'] = None
    annotation_df['origin_role'] = None
    annotation_df['destination_role'] = None

# Begin looping over the rows of the input DataFrame. Enumerate the result to
# show annotation progress to the user.
for i, (ix, row) in enumerate(annotation_df.iterrows()):

    # Check that no annotation exists for the current row
    if row['rst_relation'] is None:

        # Extract the filename of the diagram image by splitting the string at
        # .json and taking the first item in the list, which is the image name.
        image_filename = row['filename'].split('.json')[0]

        # Define path to diagram image
        image_path = os.path.join(images_path, image_filename)

        # Read the image using OpenCV
        image = cv2.imread(image_path)

        # Begin extracting information about the semantic relation, starting
        # with the origin and destination.
        origin = row['origin']
        destination = row['destination']

        # Extract information on the position of the diagram elements that take
        # part in the relation. This information is contained in a dictionary
        # in the 'polygons' column.
        polygons = row['polygons']

        # Use the 'draw' function to draw the origin.
        draw(image, polygons[origin]['type'], polygons[origin]['coords'],
             'origin')

        # Use the 'draw' function to draw the destination.
        draw(image, polygons[destination]['type'],
             polygons[destination]['coords'], 'destination')

        # Resize the image for better visualization. Begin by calculating aspect
        # ratio (target width / current width) and new width of the image.
        ratio = 800.0 / image.shape[1]
        size = (800, int(image.shape[0] * ratio))

        # Resize the preview image
        preview = cv2.resize(image, size, interpolation=cv2.INTER_AREA)

        # Show the image
        cv2.imshow("{} - {}/{}".format(image_filename, i+1, len(annotation_df)),
                   preview)

        # Print status to user.
        print("Press any key in the window displaying the image to continue.")

        # Wait for user input
        cv2.waitKey()

        # Begin the annotation by clearing the screen
        os.system('cls' if os.name == 'nt' else 'clear')

        # Request the user to determine the relationship between the elements by
        # presenting the standard question about the relationship (rel_q)
        rel = input(rel_q)

        # Check that the input entered by the user is a relation or a request
        # for more information.
        while rel not in rel_dict:
            # If the user requests additional information on the available
            # commands, print the information.
            if rel == 'info':
                # Print available commands and present the question again
                rel = print_info(rel_q, 'info')
            if rel == 'rels':
                # Print information on RST relations and present the question
                rel = print_info(rel_q, 'rels')
            # If requested, exit the program
            if rel == 'quit':
                print("Quitting.")
                exit()
            # If the input is not a valid relation or a request for more info,
            # then ignore the input and present the standard question again
            else:
                print("Sorry, that is not a valid relation.")
                rel = input(rel_q)

        # Append the RST annotation to the DataFrame at the current index
        annotation_df.at[ix, 'rst_relation'] = rel

        # If the RST relation was annotated as 'none', set both values for
        # nuclearity also to 'none' and continue
        if rel == 'none':
            annotation_df.at[ix, 'origin_role'] = 'none'
            annotation_df.at[ix, 'destination_role'] = 'none'
            # Close the window
            cv2.destroyAllWindows()
            continue

        # Then ask the standard question about nuclei and satellites. Begin by
        # clearing the screen, then pose the question for the origin.
        os.system('cls' if os.name == 'nt' else 'clear')
        origin_role = input(origin_q)

        # Again, check that the input is valid, either 'nucleus', 'satellite' or
        # their valid abbreviation ('nuc' or 'sat').
        while origin_role not in nuc_dict:
            # If the user requests additional information, print the information
            # and present the question again.
            if origin_role == 'info':
                origin_role = print_info(origin_q, 'info')
            # If the input is not valid, print a message and repeat question
            else:
                print("Sorry, that is not a valid role for nuclearity.")
                origin_role = input(origin_q)

        # When a valid entry is entered, enter the value to the DataFrame
        if origin_role in ['n', 'nuc', 'nucleus']:
            annotation_df.at[ix, 'origin_role'] = 'nucleus'
        if origin_role in ['s', 'sat', 'satellite']:
            annotation_df.at[ix, 'origin_role'] = 'satellite'

        # Next, do the same for the destination element. Clear screen first.
        os.system('cls' if os.name == 'nt' else 'clear')
        dest_role = input(dest_q)

        # Check that the input is valid
        while dest_role not in nuc_dict:
            # If additional information is requested, print and repeat question
            if dest_role == 'info':
                dest_role = print_info(dest_q, 'info')
            # If the input is not valid, print a message and repeat question
            else:
                print("Sorry, that is not a valid role for nuclearity.")
                dest_role = input(dest_q)

        # When a valid entries have been entered, enter their values into to the
        # DataFrame.
        if origin_role in ['n', 'nuc', 'nucleus']:
            annotation_df.at[ix, 'origin_role'] = 'nucleus'
        if origin_role in ['s', 'sat', 'satellite']:
            annotation_df.at[ix, 'origin_role'] = 'satellite'
        if dest_role in ['n', 'nuc', 'nucleus']:
            annotation_df.at[ix, 'destination_role'] = 'nucleus'
        if dest_role in ['s', 'sat', 'satellite']:
            annotation_df.at[ix, 'destination_role'] = 'satellite'

        # Close the window
        cv2.destroyAllWindows()

        # Save the DataFrame to disk to save the annotation
        annotation_df.to_pickle(output_path)
