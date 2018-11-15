# -*- coding: utf-8 -*-

from .annotate import *
from .draw import *
from .interface import *
from .parse import *

import cv2
import numpy as np
import os


class Diagram:
    """
    This class holds the annotation for a single AI2D-RST diagram.
    """
    def __init__(self, ai2d_ann, image):
        """
        This function initializes the Diagram class.
        
        Parameters:
            ai2d_ann: Path to the JSON file containing the original AI2D
                      annotation or a dictionary containing parsed annotation.
            image: Path to the image file containing the diagram.

        Returns:
            An AI2D Diagram object with various methods and attributes.
        """
        # Mark all annotation layers initially as incomplete
        self.complete = False
        self.group_complete = False  # grouping (hierarchy + macro)
        self.connectivity_complete = False  # connectivity
        self.rst_complete = False  # rst

        # Set image path
        self.image_filename = image

        # Continue by checking the annotation type. If the input is a dictionary
        # assign the dictionary to the variable 'annotation'.
        if type(ai2d_ann) == dict:
            self.annotation = ai2d_ann

        else:
            # Read the JSON annotation into a dictionary
            self.annotation = load_annotation(ai2d_ann)

        # Create a graph for layout annotation (hierarchy and macro grouping)
        self.layout_graph = create_graph(self.annotation,
                                         edges=False,
                                         arrowheads=False,
                                         mode='layout'
                                         )

        # Set up placeholders for connectivity and RST layers
        self.connectivity_graph = None
        self.rst_graph = None

        # Set up a placeholder for comments
        self.comments = []

        # Set up a flag for tracking updates to the graph (for drawing)
        self.update = False

    def annotate_layout(self, review):
        """
        A function for annotating the logical / layout structure (DPG-L) of a
        diagram. This function covers both content hierarchy and macro-grouping.
        
        Parameters:
            review: A Boolean defining whether review mode is active or not.
        
        Returns:
            Updates the graph contained in the Diagram object
            (self.layout_graph) according to the user input.
        """

        # If review mode is active, unfreeze the layout graph
        if review:

            # Unfreeze the layout graph by making a copy
            self.layout_graph = self.layout_graph.copy()

        # Visualize the layout segmentation
        segmentation = draw_layout(self.image_filename, self.annotation, 480)

        # Draw the graph
        diagram = draw_graph(self.layout_graph, dpi=100, mode='layout')

        # Set up flags for tracking whether annotation should be hidden or shown
        show = False
        hide = False

        # Enter a while loop for the annotation procedure
        while not self.group_complete:

            # Check if the graph needs to be updated
            if self.update:

                # Re-draw the graph
                diagram = draw_graph(self.layout_graph, dpi=100, mode='layout')

                # Mark update complete
                self.update = False

            # Check if segmentation annotation is hidden and should be re-drawn
            if hide and show:

                # Visualize the layout segmentation
                segmentation = draw_layout(self.image_filename, self.annotation,
                                           480)

                # Return to normal mode by setting both hide and show to False
                hide = False
                show = False

            # Join the graph and the layout structure horizontally
            preview = np.hstack((diagram, segmentation))

            # Show the resulting visualization
            cv2.imshow("Annotation", preview)

            # Prompt user for input
            user_input = input(prompts['layout_default'])

            # Escape accidental / purposeful carrier returns without input
            if len(user_input.split()) == 0:

                continue

            # Check if the input is a generic command
            if user_input in commands['generic']:

                # Send the command to the interface along with current graph
                process_command(user_input,
                                mode='layout',
                                diagram=self,
                                current_graph=self.layout_graph)

                # If the user wants to move on the next diagram without saving
                # the annotation, break from the while loop.
                if user_input == 'next':

                    break

                # Otherwise continue
                continue

            # Hide/show layout segmentation if requested
            if user_input == 'hide':

                # If hide is False, re-draw the layout without annotation
                if not hide:

                    # Re-draw the layout
                    segmentation = draw_layout(self.image_filename,
                                               self.annotation,
                                               480, hide=True)

                    # Flag the annotation as hidden
                    hide = True

                    continue

                # If the layout is already hidden, re-draw the annotation
                if hide:

                    # Set show to True
                    show = True

                    continue

            # Print the names of macro groups if requested
            if user_input == 'macrogroups':

                # Print header
                print("\nAvailable macro groups and their aliases\n---")

                # Print the available macro groups and their aliases
                for k, v in macro_groups.items():
                    print("{} (alias: {})".format(v, k))

                # Print closing line
                print("---\n")

                continue

            # Check if the user has requested to describe a macro-grouping
            if 'macro' == user_input.split()[0]:

                # Check the length of the input
                if len(user_input.split()) < 2:

                    # Print error message
                    print("[ERROR] You must input at least one identifier in "
                          "addition to the command 'macro'.")

                    continue

                # Prepare input for validation
                user_input = prepare_input(user_input, 1)

                # Check the input against the current graph
                valid = validate_input(user_input, self.layout_graph)

                # If the input is not valid, continue
                if not valid:

                    continue

                # Proceed if the user input is valid
                if valid:

                    # Generate a dictionary mapping group aliases to IDs
                    group_dict = replace_aliases(self.layout_graph)

                    # Replace aliases with valid identifiers, if used
                    user_input = [group_dict[u] if u in group_dict.keys()
                                  else u for u in user_input]

                    # Assign macro groups to nodes
                    macro_group(self.layout_graph, user_input)

                    continue

            # Check if the user has requested to delete a grouping node
            if 'rm' in user_input:

                # Prepare input for validation
                user_input = prepare_input(user_input, 1)

                # Check the input against the current graph
                valid = validate_input(user_input, self.layout_graph)

                # If the input is not valid, continue
                if not valid:

                    continue

                # Proceed if the user input is valid
                if valid:

                    # Generate a dictionary mapping group aliases to IDs
                    group_dict = replace_aliases(self.layout_graph)

                    # Replace aliases with valid identifiers, if used
                    user_input = [group_dict[u] if u in group_dict.keys()
                                  else u for u in user_input]

                    # Update the graph according to user input
                    self.layout_graph.remove_nodes_from(user_input)

                    # Flag the graph for re-drawing
                    self.update = True

                    continue

            # Check if the user has requested to remove edges connected to node
            if 'free' in user_input:

                # Prepare input for validation
                user_input = prepare_input(user_input, 1)

                # Check the input against the current graph
                valid = validate_input(user_input, self.layout_graph)

                # If the input is not valid, continue
                if not valid:

                    continue

                # If the input is valid, proceed
                if valid:

                    # Generate a dictionary mapping group aliases to IDs
                    group_dict = replace_aliases(self.layout_graph)

                    # Replace aliases with valid identifiers, if used
                    user_input = [group_dict[u] if u in group_dict.keys()
                                  else u.upper() for u in user_input]

                    # Collect a list of edges to delete
                    edge_bunch = list(self.layout_graph.edges(user_input))

                    # Remove designated edges from the layout graph
                    self.layout_graph.remove_edges_from(edge_bunch)

                    # Flag the graph for re-drawing
                    self.update = True

            # If user input does not include a valid command, assume the input
            # is a string containing a list of diagram elements.
            elif user_input not in commands['generic']:

                # Prepare input for validation
                user_input = prepare_input(user_input, 0)

                # Check the input against the current graph
                valid = validate_input(user_input, self.layout_graph)

                # If the input is not valid, continue
                if not valid:

                    continue

                # Proceed if the user input is valid
                if valid:

                    # Check input length
                    if len(user_input) == 1:

                        # Print error message
                        print("Sorry, you must enter more than one identifier "
                              "to form a group.")

                        continue

                    # Proceed if aufficient number of valid elements is provided
                    elif len(user_input) > 1:

                        # Generate a dictionary mapping group aliases to IDs
                        group_dict = replace_aliases(self.layout_graph)

                        # Replace aliases with valid identifiers, if used
                        user_input = [group_dict[u]
                                      if u.lower() in group_dict.keys()
                                      else u for u in user_input]

                        # Update the graph according to user input
                        group_nodes(self.layout_graph, user_input)

                        # Flag the graph for re-drawing
                        self.update = True

                # Continue until the annotation process is complete
                continue

    def annotate_connectivity(self, review):
        """
        A function for annotating a diagram for its connectivity.

        Parameters:
            review: A Boolean defining whether review mode is active or not.

        Returns:
            Updated the graph contained in the Diagram object
            (self.connectivity_graph) according to the user input.
        """
        # If review mode is active, unfreeze the layout graph
        if review:

            # Unfreeze the layout graph by making a copy
            self.connectivity_graph = self.connectivity_graph.copy()

        # Visualize the layout segmentation
        segmentation = draw_layout(self.image_filename, self.annotation, 480)

        # If the connectivity graph does not exist, populate graph
        if self.connectivity_graph is None:

            # Create an empty MultiDiGraph
            self.connectivity_graph = nx.MultiDiGraph()

            # Create a temporary copy of the layout graph for filtering content
            temp_graph = self.layout_graph.copy()

            # Get a dictionary of nodes and a list of edges
            nodes = dict(temp_graph.nodes(data=True))
            edges = list(temp_graph.edges())

            # Fetch a list of edges to/from imageConsts
            iconst_edges = [(s, t) for (s, t) in edges
                            if nodes[s]['kind'] == 'imageConsts'
                            or nodes[t]['kind'] == 'imageConsts']

            # Remove grouping edges using the list
            temp_graph.remove_edges_from(iconst_edges)

            # Use the isolates function to locate grouping nodes for groups
            isolates = list(nx.isolates(temp_graph))

            # Remove isolated grouping nodes
            isolates = [i for i in isolates if nodes[i]['kind']
                        in ['group', 'imageConsts']]

            # Remove isolated nodes from the graph
            temp_graph.remove_nodes_from(isolates)

            # Add attributes to the remaining edges
            nx.set_edge_attributes(temp_graph, 'grouping', 'kind')

            # Add the filtered nodes and edgesto the connectivity graph
            self.connectivity_graph.add_nodes_from(temp_graph.nodes(data=True))
            self.connectivity_graph.add_edges_from(temp_graph.edges(data=True))

        # Draw the graph using the layout mode
        diagram = draw_graph(self.connectivity_graph, dpi=100,
                             mode='connectivity')

        # Set up flags for tracking whether annotation should be hidden or shown
        show = False
        hide = False

        # Enter a while loop for the annotation procedure
        while not self.connectivity_complete:

            # Check if the graph needs to be updated
            if self.update:

                # Close previous plot
                plt.close()

                # Re-draw the graph using the layout mode
                diagram = draw_graph(self.connectivity_graph, dpi=100,
                                     mode='connectivity')

                # Mark update complete
                self.update = False

            # Check if segmentation annotation is hidden and should be re-drawn
            if hide and show:

                # Visualize the layout segmentation
                segmentation = draw_layout(self.image_filename, self.annotation,
                                           480)

                # Return to normal mode by setting both hide and show to False
                hide = False
                show = False

            # Join the graph and the layout structure horizontally
            preview = np.hstack((diagram, segmentation))

            # Show the resulting visualization
            cv2.imshow("Annotation", preview)

            # Prompt user for input
            user_input = input(prompts['conn_default'])

            # Escape accidental / purposeful carrier returns without input
            if len(user_input.split()) == 0:

                continue

            # Check if the user input is a generic command
            if user_input in commands['generic']:

                # Send the command to the interface along with current graph
                process_command(user_input,
                                mode='connectivity',
                                diagram=self,
                                current_graph=self.connectivity_graph)

                # If the user wants to move on the next diagram without saving
                # the annotation, break from the while loop.
                if user_input == 'next':

                    break

                # Otherwise continue
                continue

            # Hide/show layout segmentation if requested
            if user_input == 'hide':

                # If hide is False, re-draw the layout without annotation
                if not hide:

                    # Re-draw the layout
                    segmentation = draw_layout(self.image_filename,
                                               self.annotation,
                                               480, hide=True)

                    # Flag the annotation as hidden
                    hide = True

                    continue

                # If the layout is already hidden, re-draw the annotation
                if hide:

                    # Set show to True
                    show = True

                    continue

            # Check if grouping edges are to be hidden
            if user_input == 'ungroup':

                # Retrieve a list of edges in the graph
                edge_bunch = list(self.connectivity_graph.edges(data=True))

                # Collect grouping edges from the edge list
                edge_bunch = [(u, v) for (u, v, d) in edge_bunch
                              if d['kind'] == 'grouping']

                # Remove grouping edges from the connectivity graph
                self.connectivity_graph.remove_edges_from(edge_bunch)

                # Flag the graph for re-drawing
                self.update = True

            # If user input does not include a valid command, assume the input
            # is a string defining a connectivity relation.
            elif user_input not in commands['generic']:

                # Set a flag for tracking connections
                connection_found = False

                # Define connection type aliases and their names
                connection_types = {'-': 'undirectional',
                                    '>': 'directional',
                                    '<>': 'bidirectional'}

                # Split the input into a list
                user_input = user_input.split(' ')

                # Strip extra whitespace
                user_input = [u.strip() for u in user_input]

                # Loop over connection types and check them against the input
                for alias in connection_types.keys():

                    # If a match is found, record its index in user input
                    if alias in user_input:

                        # Get connection index and type; assign to variable
                        connection_ix = user_input.index(alias)
                        connection_type = connection_types[alias]

                        # Use connection index to get source and target sets
                        source = user_input[:connection_ix]
                        target = user_input[connection_ix + 1:]

                        # Strip possible extra commas from sources and targets
                        source = [x.strip(',') for x in source]
                        target = [x.strip(',') for x in target]

                        # Check the input against the current graph
                        valid = validate_input(source + target,
                                               self.connectivity_graph)

                        # If the user input is not valid, continue
                        if not valid:

                            continue

                        # If the user input is valid, proceed
                        if valid:

                            # Set connection tracking flag to True
                            connection_found = True

                            continue

                # If a valid connection type is found, create a new connection
                if connection_found:

                    # Initialize a list for edge tuples
                    edge_bunch = []

                    # Generate a dictionary mapping group aliases to IDs
                    group_dict = replace_aliases(self.connectivity_graph)

                    # Update the group identifiers in sources and targets to use
                    # valid identifiers, not the G-prefixed aliases
                    source = [group_dict[s] if s in group_dict.keys() else s
                              for s in source]
                    target = [group_dict[t] if t in group_dict.keys() else t
                              for t in target]

                    # Loop over sources
                    for s in source:

                        # Loop over targets
                        for t in target:

                            # Convert identifiers to uppercase and add an edge
                            # tuple to the list of edges
                            edge_bunch.append((s.upper(), t.upper()))

                    # If the connection type is bidirectional, add arrows also
                    # from target to source.
                    if connection_type == 'bidirectional':

                        # Loop over targets
                        for t in target:

                            # Loop over sources
                            for s in source:

                                # Convert identifiers to uppercase as above and
                                # add an edge tupleto the list of edges
                                edge_bunch.append((t.upper(), s.upper()))

                    # When edges have been added for all connections, add edges
                    # from the edge list
                    self.connectivity_graph.add_edges_from(edge_bunch,
                                                           kind=connection_type)

                    # Flag the graph for re-drawing
                    self.update = True

            # Continue until the annotation process is complete
            continue

    def annotate_rst(self, review):
        """
        A function for annotating the rhetorical structure (DPG-R) of a diagram.
        
        Parameters:
            review: A Boolean defining whether review mode is active or not.
        
        Returns:
            Updates the RST graph in the Diagram object (self.rst_graph).
        """
        # If review mode is active, unfreeze the layout graph
        if review:

            # Unfreeze the layout graph by making a copy
            self.rst_graph = self.rst_graph.copy()

        # Visualize the layout segmentation
        segmentation = draw_layout(self.image_filename, self.annotation, 480)

        # If the connectivity graph does not exist, populate graph
        if self.rst_graph is None:

            # Retrieve a list of valid nodes from the layout graph
            nodes = list(self.layout_graph.nodes(data=True))

            # Remove groups from the list of nodes
            nodes = [n for n in nodes if n[1]['kind'] != 'group']

            # Populate the RST graph according to the list of nodes
            self.rst_graph = create_graph(nodes,
                                          edges=False,
                                          arrowheads=False,
                                          mode='rst')

        # Draw the graph using RST mode
        diagram = draw_graph(self.rst_graph, dpi=100, mode='rst')

        # Enter a while loop for the annotation procedure
        while not self.rst_complete:

            # Check if the graph needs to be updated
            if self.update:

                # Re-draw the graph
                diagram = draw_graph(self.rst_graph, dpi=100, mode='rst')

                # Mark update complete
                self.update = False

            # Join the graph and the layout structure horizontally
            preview = np.hstack((diagram, segmentation))

            # Show the resulting visualization
            cv2.imshow("Annotation", preview)

            # Prompt user for input
            user_input = input(prompts['rst_default'])

            # Escape accidental / purposeful carrier returns without input
            if len(user_input.split()) == 0:

                continue

            # Check the input
            if user_input in commands['generic']:

                # Send the command to the interface along with current graph
                process_command(user_input,
                                mode='rst',
                                diagram=self,
                                current_graph=self.rst_graph)

                # If the user wants to move on the next diagram without saving
                # the annotation, break from the while loop.
                if user_input == 'next':

                    break

                # Otherwise continue
                continue

            # If the user requests a list of available RST relations, print
            # the keys and their definitions.
            if user_input == 'rels':

                # Clear screen first
                os.system('cls' if os.name == 'nt' else 'clear')

                # Loop over RST relations
                for k, v in rst_relations.items():

                    # Print information on each RST relation
                    print("{} - abbreviation: {}, type: {}.".format(
                        v['name'].upper(),
                        k,
                        v['kind']))

                continue

            # If the user input is a new relation, request additional input
            if user_input == 'new':

                # Request relation name
                relation = input(prompts['rel_prompt'])

                # Strip extra whitespace and convert the input to lowercase
                relation = relation.strip().lower()

                # Check that the input is a valid relation
                if relation in rst_relations.keys():

                    # Create a rhetorical relation and add to graph
                    create_relation(self.rst_graph, relation)

                    # Flag the graph for re-drawing
                    self.update = True

                else:
                    print("Sorry, {} is not a valid relation."
                          .format(relation))

            if user_input not in commands['rst']:

                # Print error message
                print("Sorry, {} is not a valid command.".format(user_input))

                continue

            # Continue until the annotation process is complete
            continue
