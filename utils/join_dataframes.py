# -*- coding: utf-8 -*-

# Import the necessary packages
import argparse
import glob
import pandas as pd

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the directory containing the DataFrames to join.")
ap.add_argument("-o", "--output", required=True,
                help="Path to the combined DataFrame.")
ap.add_argument("-p", "--purge", required=False, action="store_true",
                help="Remove diagrams marked as candidates for deletion.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
input_dir = args['input']
output_df = args['output']

# Set up a placeholder list for DataFrames
dfs = []

# Get the files in the input directory
for f in glob.glob(input_dir + '*.pkl'):

    # Print status
    print("[INFO] Adding {} to the DataFrame ...".format(f))

    # Read DataFrame
    df = pd.read_pickle(f)

    # Append pickle to list
    dfs.append(df)

# Concatenate DataFrames in the list
df_out = pd.concat(dfs)

# Check if the user has requested to remove diagrams marked for deletion
if args['purge']:

    # Set up placeholder list for rows to delete
    del_rows = []

    # Loop over the DataFrame rows
    for ix, row in df_out.iterrows():

        # Loop over each comment
        for comment in row['diagram'].comments:

            # If comment contains the word 'deletion' and index not in del list
            if 'deletion' in comment and ix not in del_rows:

                # Append index to list of rows to delete
                del_rows.append(ix)

    # Drop rows collected into the list
    df_out = df_out.drop(del_rows)

# Reset index
df_out = df_out.reset_index(drop=True)

# Save DataFrame
df_out.to_pickle(output_df)

# Print status
print("[DONE] Added {} diagrams to {}".format(len(df_out), output_df))
