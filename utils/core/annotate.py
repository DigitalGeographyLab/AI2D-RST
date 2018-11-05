# -*- coding: utf-8 -*-

import string
import random
from .interface import *
from .parse import *


def create_id(length=6, chars=string.ascii_uppercase+string.digits):
    """
    A function for creating random identifiers for grouping identifiers, which
    can become big enough to slowing down the drawing of graphs.

    Parameters:
        length: The requested length of the identifier.
        chars: The characters used to generate the random identifier.

    Returns:
        A random identifier of requested length.
    """
    return ''.join(random.choice(chars) for x in range(length))


def create_relation(rst_graph, user_input):
    """
    A function for drawing an RST relation between several diagram elements.

    Parameters:
        rst_graph: A NetworkX Graph.
        user_input: A string containing the name of a valid RST relation.

    Returns:
         An updated NetworkX Graph.
    """
    # Retrieve the name and kind of the RST relation
    relation_name = rst_relations[user_input]['name']
    relation_kind = rst_relations[user_input]['kind']

    # Create a dictionary of the nodes currently in the graph
    node_ix = get_node_dict(rst_graph, kind='node')

    # Generate a list of valid diagram elements present in the graph
    valid_nodes = [e.lower() for e in node_ix.keys()]

    # Generate a dictionary of RST relations present in the graph
    relation_ix = get_node_dict(rst_graph, kind='relation')

    # Loop through current RST relations and rename them for convenience.
    # This allows the user to refer to the relation identifier (e.g. r1)
    # instead of a complex relation ID (e.g. B0-T1+B9) during annotation.
    relation_ix = {"r{}".format(i): k for i, (k, v) in
                   enumerate(relation_ix.items(), start=1)}

    # Create a list of valid relation identifiers based on the dict keys
    valid_rels = [r.lower() for r in relation_ix.keys()]

    # Combine the valid nodes and relations into a single set
    valid_ids = set(valid_nodes + valid_rels)

    # Check whether the RST relation is mono- or multinuclear. Start with
    # mononuclear relations.
    if relation_kind == 'mono':

        # Request the identifier of the nucleus in the RST relation
        nucleus = input(prompts['nucleus_id'])

        # Split the user input into a list and convert to lowercase
        nucleus = nucleus.split()
        nucleus = [n.lower() for n in nucleus]

        # Check the total number of inputs in the list
        if len(nucleus) != 1:

            # Print error message and return
            print(messages['nucleus_err'])

            return

        # Check the user input against the set of valid identifiers
        if not set(nucleus).issubset(valid_ids):

            # If the user input is not a subset of valid identifiers, print
            # error message and return
            print("Sorry, {} is not a valid identifier. Please try "
                  "again.".format(nucleus))

            return

        else:

            # The input is valid, continue to process satellites
            pass

        # Request the identifier(s) of the satellite(s) in the RST relation
        satellites = input(prompts['satellite_id'])

        # Split the user input into a list and convert to lowercase
        satellites = satellites.split()
        satellites = [s.lower() for s in satellites]

        # Check the user input against the set of valid identifiers
        if not set(satellites).issubset(valid_ids):

            # Get difference between user input and valid graph
            diff = set(satellites).difference(valid_ids)

            # If the user input is not a subset of valid identifiers, print
            # error message and return
            print("Sorry, {} is not a valid diagram element or command."
                  " Please try again.".format(' '.join(diff)))

            return

        else:

            # If the input is valid, generate a name for the new relation
            new_relation = ''.join(nucleus).upper() + '-' + \
                           '+'.join(satellites).upper()

            # Add a new node to the graph to represent the RST relation
            rst_graph.add_node(new_relation,
                               kind='relation',
                               nucleus=nucleus,
                               satellites=satellites,
                               rel_name=relation_name,
                               id=new_relation
                               )

            # Draw edges from satellite(s) to the current RST relation
            for s in satellites:

                # Check if the satellites include another RST relation
                if s in relation_ix.keys():

                    # Fetch the origin node from the dictionary of relations
                    satellite_rel = relation_ix[s]

                    # Add edge from satellite relation to the new relation
                    rst_graph.add_edge(satellite_rel, new_relation,
                                       kind='satellite')

                # If the satellite is not a relation, draw edge from node
                else:

                    # Add edge to graph
                    rst_graph.add_edge(s.upper(), new_relation,
                                       kind='satellite')

            # Draw edges from nucleus to relation
            for n in nucleus:

                # Add edge to graph
                rst_graph.add_edge(new_relation, n.upper(),
                                   kind='nucleus')

    # Continue by checking if the relation is multinuclear
    if relation_kind == 'multi':

        # Request the identifiers of the nuclei in the RST relation
        nuclei = input(prompts['nuclei_id'])

        # Split the user input into a list and convert to lowercase
        nuclei = nuclei.split()
        nuclei = [n.lower() for n in nuclei]

        # Check the total number of inputs in the list
        if len(nuclei) <= 1:

            # Print error message and return
            print(messages['nuclei_err'])

            return

        # Check the user input against the set of valid identifiers
        if not set(nuclei).issubset(valid_ids):

            # Get the difference between user input and valid ID sets
            diff = set(nuclei).difference(valid_ids)

            # Print error message with difference in sets
            print("Sorry, {} is not a valid diagram element or command. "
                  "Please try again.".format(' '.join(diff)))

            return

        # If the input is valid, continue to draw the relations
        else:

            # Generate a name for the new relation
            new_relation = '+'.join(nuclei).upper()

            # Add a new node to the graph to represent the RST relation
            rst_graph.add_node(new_relation,
                               kind='relation',
                               nuclei=nuclei,
                               rel_name=relation_name,
                               id=new_relation)

            # Draw edges from nuclei to the current RST relation
            for n in nuclei:

                # Check if the nuclei include another RST relation
                if n in relation_ix.keys():

                    # Fetch the origin node from the relation index
                    origin = relation_ix[n]

                    # Add edge from the RST relation acting as nuclei to the
                    # current RST relation
                    rst_graph.add_edge(new_relation, origin,
                                       kind='nucleus')

                # If all nuclei are nodes, draw edges to the RST relation
                else:

                    # Add edge to graph
                    rst_graph.add_edge(new_relation, n.upper(),
                                       kind='nucleus')


def group_nodes(graph, user_input):
    """
    A function for grouping together nodes of a graph, which are included in
    the accompanying list.

    Parameters:
        graph: A NetworkX Graph.
        user_input: A list of valid nodes in the graph.

    Returns:
        An updated NetworkX Graph.
    """
    # Create a dictionary of nodes in the graph
    node_dict = get_node_dict(graph)

    # Check user input against the node dictionary for input types
    input_node_types = [node_dict[u.upper()] for u in user_input]

    # If the user input contains an imageConsts, do not add a node
    if 'imageConsts' in input_node_types:

        for k, v in node_dict.items():

            if v == 'imageConsts':

                for valid_elem in user_input:

                    graph.add_edge(valid_elem.upper(), k.upper())

    else:
        # Generate a name for the new node that joins together the elements
        # provided by the user
        new_node = create_id()

        # Add the new node to the graph
        graph.add_node(new_node, kind='group')

        # Add edges from nodes in the user input to the new node
        for valid_elem in user_input:

            graph.add_edge(valid_elem.upper(), new_node)


def macro_group(graph, user_input):
    """
    A function for assigning macro-grouping information to nodes in the graph.

    Parameters:
        graph: A NetworkX Graph.
        user_input: A list of valid nodes in the graph.

    Returns:
        An updated NetworkX graph.
    """
    # Request macro grouping type:
    macro_group_type = input(prompts['macro_group'])

    # Flatten a dictionary of valid macro groups and their abbreviations
    valid_macro_groups = list(macro_groups.keys()) + list(macro_groups.values())

    # Check for valid macro group type
    if macro_group_type not in valid_macro_groups:

        # Print error message
        print("Sorry, {} is not a valid macro group."
              " Please try again.".format(macro_group_type))

        return

    # If the input is valid, add macro grouping information to the nodes
    if macro_group_type in valid_macro_groups:

        # Check if formatting is needed in case the input is an abbreviation
        if macro_group_type in list(macro_groups.keys()):

            # Update the macro group name to the full name
            macro_group_type = macro_groups[macro_group_type]

        # Generate a matching list of grouping information
        group_list = [macro_group_type for x in range(0, len(user_input))]

        # Convert user input to uppercase
        user_input = [x.upper() for x in user_input]

        # Create a dictionary from user input; convert to uppercase
        macro_grouping = dict(zip(user_input, group_list))

        # Add macro grouping information to the graph nodes
        nx.set_node_attributes(graph, macro_grouping, 'macro_group')

        # TODO Add information on tables
