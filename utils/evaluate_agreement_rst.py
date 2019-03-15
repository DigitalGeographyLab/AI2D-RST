# -*- coding: utf-8 -*-

"""
This script loads examples from the RST annotation in the AI2D-RST dataset and
presents them to the annotator. The resulting description is used for measuring
agreement between the annotators.

To continue annotation from a previous session, give the path to the existing
DataFrame to the -o/--output argument.

Usage:
    python evaluate_agreement_connectivity.py -a annotation.pkl -o output.pkl
    -s sample.pkl -i path_to_ai2d_images/

Arguments:
    -a/--annotation: Path to the pandas DataFrame containing AI2D-RST Diagram
                     objects.
    -s/--sample: Path to the file containing data sampled from the AI2D-RST
                 Diagram objects.
    -i/--images: Path to the directory containing the AI2D diagram images.
    -o/--output: Path to the output file, in which the resulting annotation is
                 stored.

Returns:
    A pandas DataFrame containing the annotation stored in the input DataFrame
    and the annotation created using this script.
"""

# Import packages
from colorama import Fore, Style, init
from core.draw import *
from core.interface import rst_relations
from pathlib import Path
import argparse
import cv2
import os
import pandas as pd


# Initialize colorama
init()

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-s", "--sample", required=True)
ap.add_argument("-a", "--annotation", required=True)
ap.add_argument("-i", "--images", required=True)
ap.add_argument("-o", "--output", required=True)

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
sample_path = args['sample']
images_path = args['images']
output_path = args['output']

# Verify the input paths, print error and exit if not found
if not Path(ann_path).exists():

    exit("[ERROR] Cannot find {}. Check the input to -a!".format(ann_path))

if not Path(images_path).exists():

    exit("[ERROR] Cannot find {}. Check the input to -i!".format(images_path))

# Check if the output file exists already, or whether to continue with previous
# annotation.
if os.path.isfile(output_path):

    # Read existing files
    annotation_df = pd.read_pickle(ann_path)
    sample = pd.read_pickle(output_path)

    # Print status message
    print("[INFO] Continuing existing annotation in {}.".format(output_path))

# Otherwise, read the annotation from the input DataFrame
if not os.path.isfile(output_path):

    # Make a copy of the input DataFrame
    annotation_df = pd.read_pickle(ann_path).copy()

    # Load DataFrame containing sample
    sample = pd.read_pickle(sample_path)

# Define prompts for user input
rst_prompt = Fore.RED + "[RST] What kind of relation holds between the " \
                        "nucleus (red) and satellites (blue) or nuclei " \
                        "(green)? " + Style.RESET_ALL

# Define a list of annotator commands
commands = ['help', 'exit']

# Begin looping over the sample and presenting the relations to the user
for i, (ix, row) in enumerate(sample.iterrows(), start=1):

    # Check if annotation has already been performed
    try:
        if row['annotation'] in [v['name'] for k, v in rst_relations.items()]:

            continue

    except KeyError:
        pass

    # Begin the annotation by clearing the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Set annotation completeness initially to False
    annotation_complete = False

    # Fetch the filename of current diagram image
    image_name = row['image_name']

    # Join with path to image directory with current filename
    image_path = os.path.join(images_path, row['image_name'])

    # Print status message
    print(Fore.YELLOW + "[INFO] Now processing RST relation {}/{} from {}."
          .format(i, len(sample), image_name) + Style.RESET_ALL)

    # Fetch the layout annotation from the original DataFrame
    original_row = annotation_df.loc[annotation_df['image_name'] == image_name]

    # Get the annotation dictionary for the original AI2D annotation
    annotation = original_row['annotation'].item()

    # Get the AI2D Diagram object
    diagram = original_row['diagram'].item()

    # Check relation type: if nuclei is None, the relation is asymmetric.
    if row['nuclei'] is None:

        # Get nucleus and satellites and split into lists
        nucleus = row['nucleus'].split()
        satellites = row['satellites'].split()

        # Generate highlights dictionary
        highlight = {'red': nucleus, 'blue': satellites}

    # Otherwise, the relation must be symmetric.
    else:

        # Get nuclei and split into list
        nuclei = row['nuclei'].split()

        # Generate highlights dictionary
        highlight = {'green': nuclei}

    # Draw the annotation and highlight the source and the target
    segmentation = draw_layout(image_path, annotation, height=480,
                               highlight=highlight)

    # Show the annotation
    cv2.imshow("Annotation", segmentation)

    # Enter a while loop for performing annotation
    while not annotation_complete:

        # Set command to None
        command = None

        # Ask for initial input
        is_rst = input(rst_prompt)

        # Check if the input string is a command
        if is_rst in commands:

            # Set command variable
            command = is_rst

        # If the input string is a valid shorthand code for an RST relation
        if is_rst in rst_relations.keys():

            # Fetch the connection from the list
            relation = rst_relations[is_rst]['name']

            # Save the input to DataFrame
            sample.at[ix, 'annotation'] = str(relation)

            # Set annotation to complete
            annotation_complete = True

        # Check if user requests help
        if command == 'help':

            print(Fore.YELLOW + "[INFO] VALID RELATIONS INCLUDE: " +
                  Style.RESET_ALL)

            # Loop over the Gestalt principles and print information
            for k, v in rst_relations.items():
                print(Fore.YELLOW + "[INFO] {} ({})".format(k, v['name'])
                      + Style.RESET_ALL)

            # Reset command variable
            command = None

        # Check if the user wants to exit the annotator
        if command == 'exit':

            # Print status
            print(Fore.YELLOW + "[INFO] Saving annotation and "
                                "exiting the tool." + Style.RESET_ALL)

            # Save annotation file
            sample.to_pickle(output_path)

            # Exit the annotator
            exit()

# Save the output DataFrame
sample.to_pickle(output_path)

# Print status
print(Fore.RED + "[INFO] Annotation completed!" + Style.RESET_ALL)
