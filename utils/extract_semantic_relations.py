# -*- coding: utf-8 -*-

"""
This script extracts information about semantic relations defined in the AI2D
annotation and stores them into a single pandas DataFrame for sampling the data.

Usage:
    python extract_semantic_relations.py -a annotation -o output.pkl

Arguments:
    -a/--annotation: Path to directory containing the AI2D annotation files in JSON.
    -o/--output: Path to the output file, which contains the pandas DataFrame.

Returns:
    A pandas DataFrame stored into the output file.
"""

# Import packages
import argparse
import json
import os
import numpy as np
import pandas as pd

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-a", "--annotation", required=True)
ap.add_argument("-o", "--output", required=True)

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
ann_path = args['annotation']
output_path = args['output']

# Set up a counter to track the number of semantic relations defined in AI2D
# annotation. Also set up a list to hold the file paths to the annotation files
# for the next loop after counting the relations.
df_index_counter = 0
annotation_paths = []

# Walk through the directory containing the annotations
for (ann_root, ann_dirs, ann_files) in os.walk(ann_path):
    # Loop over the files
    for f in ann_files:
        # Process JSON files only
        if f.split('.')[-1] == 'json':

            # Define the path to the annotation file and append to the list
            annotation_path = os.path.join(ann_root, f)
            annotation_paths.append(annotation_path)

            # Load the AI2D annotation stored in the JSON file
            with open(annotation_path) as annotation_file:

                # Assign the annotation to variable 'ann'
                ann = json.load(annotation_file)

                # Increment counter
                df_index_counter += len(ann['relationships'])

# Set up a pandas DataFrame to hold the annotation
annotation_df = pd.DataFrame(index=(np.arange(0, df_index_counter)),
                             columns={"filename": str, "relation_id": str,
                                      "category": str, "origin": str,
                                      "destination": str, "connector": str,
                                      "directionality": bool, "polygons": dict})

# Set up yet another counter in order to assign the relation information to the
# appropriate index in the pandas DataFrame.
current_index = 0

# Begin looping over the annotation in the JSON files to populate the dataframe
for path in annotation_paths:

    # Split the current filename from the path
    filename = path.split('/')[-1]

    # Load the AI2D annotation stored in the JSON file
    with open(path) as annotation_file:

        # Assign the annotation to variable 'ann'
        ann = json.load(annotation_file)

        # Next, begin processing the annotation for semantic relations
        for relation in ann['relationships']:

            # Set up a dictionary for holding information on the polygons
            polygon_dict = {}

            # Append current filename
            annotation_df.at[current_index, 'filename'] = filename

            # Extract detailed information about the defined relation
            relation_id = ann['relationships'][relation]['id']
            relation_cat = ann['relationships'][relation]['category']
            relation_org = ann['relationships'][relation]['origin']
            relation_dest = ann['relationships'][relation]['destination']

            # Not all relations have connectors or directionality
            try:
                relation_conn = ann['relationships'][relation]['connector']
            except KeyError:
                pass
            try:
                relation_dir = ann['relationships'][relation]['hasDirectionality']
            except KeyError:
                pass

            # Append the relation information to the DataFrame
            annotation_df.at[current_index, 'relation_id'] = relation_id
            annotation_df.at[current_index, 'category'] = relation_cat
            annotation_df.at[current_index, 'origin'] = relation_org
            annotation_df.at[current_index, 'destination'] = relation_dest
            annotation_df.at[current_index, 'connector'] = relation_conn
            annotation_df.at[current_index, 'directionality'] = relation_dir

            # # Retrieve polygon information for each element
            for rel in [relation_org, relation_dest, relation_conn]:
                if rel in ann['blobs']:
                    polygon_dict[rel] = {'type': 'blob',
                                         'coords': ann['blobs'][rel]['polygon']}

                if rel in ann['text']:
                    polygon_dict[rel] = {'type': 'text',
                                         'coords': ann['text'][rel]['rectangle']}

                if rel in ann['arrows']:
                    polygon_dict[rel] = {'type': 'arrow',
                                         'coords': ann['arrows'][rel]['polygon']}

                if rel in ann['imageConsts']:
                    polygon_dict[rel] = {'type': 'entire_image',
                                         'coords': None}

            # Check that some polygon information has been collected
            if len(polygon_dict) > 0:
                annotation_df.at[current_index, 'polygons'] = polygon_dict

            # Increment current index by one
            current_index += 1

# Print status to user
print("[INFO] Extracted a total of {} relations.".format(len(annotation_df)))

# Save the pandas DataFrame to disk
annotation_df.to_pickle(output_path)

# Print status to user
print("[INFO] Done. Saved the output to {}.".format(output_path))
