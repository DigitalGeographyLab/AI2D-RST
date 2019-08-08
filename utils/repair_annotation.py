# Import packages
from colorama import Fore, Style, init
import argparse
import pandas as pd

# Initialize colorama
init()

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

# Make a copy of the input DataFrame
annotation_df = pd.read_pickle(ann_path).copy()


def repair_relation_annotation(rst_graph):

    # Get all conn_nodes
    nodes = list(rst_graph.nodes(data=True))

    # Create a node dictionary
    node_dict = {node_id: node_data for node_id, node_data in nodes}

    # Create a dictionary of relations
    rel_dict = {k: v for k, v in node_dict.items() if v['kind'] == 'relation'}

    # Set up a dictionary to hold the identifiers that need to be replaced
    replacements = {}

    # First, check the relations for references to relations acting as nucleus
    for rel_id, rel_data in rel_dict.items():

        # Begin by finding relations acting as nucleus
        try:

            # Split the nucleus attribute
            nucleus = rel_data['nucleus'].split()

            # Restrict the result to relations
            nuc_relations = [n for n in nucleus if n[0] == 'R' and len(n) != 6]

            # Check if relations have been found
            if len(nuc_relations) > 0:

                # Print status
                print(Fore.RED + "-*- detect -*- found relation {} as nucleus in asymmetric relation {} ({}).".format(' '.join(nuc_relations), rel_id, rel_data['rel_name']), Style.RESET_ALL)

                # Get edges leading away from current relation node
                nuc_edges = rst_graph.edges(rel_id, data=True)

                # Limit target to relations
                nuc_edges = [(source, target, data) for (source, target, data) in nuc_edges if node_dict[target]['kind'] == 'relation']

                # Loop over each relation
                for r, e in zip(nuc_relations, nuc_edges):

                    # Check that source (e[0]) is the current relation and
                    # the target node (e[1]) is a relation and
                    # that edge (e[2]) kind is nucleus.
                    if e[0] == rel_id and node_dict[e[1]]['kind'] == 'relation' and e[2]['kind'] == 'nucleus':

                        # Check if the replacement has been recorded
                        if r not in replacements.keys():

                            # Print status
                            print(Fore.GREEN + "-*- repair -*- changing {} to {} based on {} edge {}->{}.".format(r, e[1], e[2]['kind'], e[0], e[1]) + Style.RESET_ALL)

                            # Add identifier to the list of replacements
                            replacements[r] = e[1]

            # Replace identifiers
            nucleus = [replacements[n] if n in replacements.keys() else n for n in nucleus]

            # Join into string and set node attributes
            rst_graph.node[rel_id]['nucleus'] = ' '.join(nucleus)

        except KeyError:
            pass

        # Continue by finding relations acting as satellites
        try:

            # Split the satellites attribute
            satellites = rel_data['satellites'].split()

            # Restrict the result to relations
            sat_relations = [s for s in satellites if s[0] == 'R' and len(s) != 6]

            # Check if relations have been found
            if len(sat_relations) > 0:

                # Print status
                print(Fore.RED + "-*- detect -*- found relation(s) {} as satellites in asymmetric relation {} ({}).".format(' '.join(sat_relations), rel_id, rel_data['rel_name']) + Style.RESET_ALL)

                # Get satellite edges leading into the current relation node
                sat_edges = rst_graph.in_edges(rel_id, data=True)

                # Limit target to relations
                sat_edges = [(source, target, data) for (source, target, data) in sat_edges if node_dict[target]['kind'] == 'relation']

                # Loop over relations and edges
                for r, e in zip(sat_relations, sat_edges):

                    # Check that the target (e[1]) is the current relation
                    # and the source (e[0]) is a relation and
                    # and edge kind (e[2]) is satellite
                    if node_dict[e[0]]['kind'] == 'relation' and e[1] == rel_id and e[2]['kind'] == 'satellite':

                        # Check if the replacement has been recorded
                        if r not in replacements.keys():

                            # Print status
                            print(Fore.GREEN + "-*- repair -*- changing {} to {} based on {} edge {}->{}.".format( r, e[0], e[2]['kind'], e[1], e[0]) + Style.RESET_ALL)

                            # Add identifier to the list of replacements
                            replacements[r] = e[0]

            # Replace identifiers
            satellites = [replacements[s] if s in replacements.keys() else s for s in satellites]

            # Join into string and set node attributes
            rst_graph.node[rel_id]['satellites'] = ' '.join(satellites)

        except KeyError:
            pass

        # Finally, find relations acting as nuclei in multinuclear relations
        try:

            # Split the nuclei attribute
            nuclei = rel_data['nuclei'].split()

            # Restrict the result to relations
            mnuc_relations = [n for n in nuclei if n[0] == 'R' and len(n) != 6]

            # Check if relations have been found
            if len(mnuc_relations) > 0:

                # Print status
                print(Fore.RED + "-*- detect -*- found relation(s) {} as nuclei in symmetric relation {} ({}).".format(' '.join(mnuc_relations), rel_id, rel_data['rel_name']) + Style.RESET_ALL)

                # Get edges leading out from current relation node
                mnuc_edges = rst_graph.edges(rel_id, data=True)

                # Limit target to relations
                mnuc_edges = [(source, target, data) for (source, target, data) in mnuc_edges if node_dict[target]['kind'] == 'relation']

                # Loop over the zipped relations and edges
                for r, e in zip(mnuc_relations, mnuc_edges):

                    # Check that the source (e[0]) is the current relation and
                    # the target (e[1]) is a relation and the edge kind (e[2])
                    # is nucleus.
                    if e[0] == rel_id and node_dict[e[1]]['kind'] == 'relation' and e[2]['kind'] == 'nucleus':

                        # Check if the replacement has been recorded
                        if r not in replacements.keys():

                            # Print status
                            print(Fore.GREEN + "-*- repair -*- changing {} to {} based on {} edge {}->{}.".format(r, e[1], e[2]['kind'], e[0], e[1]), Style.RESET_ALL)

                            # Add identifier to the list of replacements
                            replacements[r] = e[1]

            # Replace identifiers
            nuclei = [replacements[n] if n in replacements.keys() else n for n in nuclei]

            # Join into string and set node attributes
            rst_graph.node[rel_id]['nuclei'] = ' '.join(nuclei)

        except KeyError:
            pass

    # Print status
    print(Fore.YELLOW + "-*- info -*- replaced {} identifiers in {} relations.".format(len(replacements), len(rel_dict)) + Style.RESET_ALL)

    # TODO Cross-check all relations referred in RST layer against valid relation IDs


# Loop over the annotation DataFrame
for ix, row in annotation_df.iterrows():

    # Assign the AI2D-RST diagram object into a variable
    diagram = row['diagram']

    print(Fore.YELLOW + "-*- info -*- now processing {} ...".format(row['image_name']) + Style.RESET_ALL)

    # Assign the RST graph into a variable
    rst_graph = diagram.rst_graph

    # Repair annotation
    repair_relation_annotation(rst_graph)

# Save the updated DataFrame
annotation_df.to_pickle(output_path)

# Print status message
print(Fore.BLUE + "-*- info -*- done! " + Style.RESET_ALL)


