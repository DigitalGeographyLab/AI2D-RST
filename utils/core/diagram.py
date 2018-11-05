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
        self.image_path = image

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

    def annotate_layout(self):
        """
        A function for annotating the logical / layout structure (DPG-L) of a
        diagram. This function covers both content hierarchy and macro-grouping.
        
        Parameters:
            None.
        
        Returns:
            Updates the graph contained in the Diagram object
            (self.layout_graph) according to the user input.
        """

        # Visualize the layout segmentation
        segmentation = draw_layout(self.image_path, self.annotation, 480)

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
                segmentation = draw_layout(self.image_path, self.annotation,
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

                continue

            # Hide/show layout segmentation if requested
            if user_input == 'hide':

                # If hide is False, re-draw the layout without annotation
                if not hide:

                    # Re-draw the layout
                    segmentation = draw_layout(self.image_path,
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

            # Check if the user has requested to describe a macro-grouping
            if 'macro' == user_input.split()[0]:

                # Check the length of the input
                if len(user_input.split()) < 2:

                    continue

                # Get the list of nodes provided by the user
                user_input = user_input.lower().split(',')[1:]

                # Strip extra whitespace
                user_input = [u.strip() for u in user_input]

                # Generate a list of valid diagram elements present in the graph
                valid_nodes = [e.lower() for e in self.layout_graph.nodes]

                # Generate a dictionary of groups
                group_dict = get_node_dict(self.layout_graph, kind='group')

                # Count the current groups and enumerate for convenience. This
                # allows the user to refer to group number instead of complex
                # identifier.
                group_dict = {"g{}".format(i): k for i, (k, v) in
                              enumerate(group_dict.items(), start=1)}

                # Create a list of identifiers based on the dict keys
                valid_groups = [g.lower() for g in group_dict.keys()]

                # Combine the valid nodes and groups into a set
                valid_elems = set(valid_nodes + valid_groups)

                # Check for invalid input by comparing the user input and the
                # valid elements as sets.
                if not set(user_input).issubset(valid_elems):

                    # Get difference between user input and valid element sets
                    diff = set(user_input).difference(valid_elems)

                    # Print error message with difference in sets.
                    print("Sorry, {} is not a valid diagram element or command."
                          " Please try again.".format(' '.join(diff)))

                    continue

                # Proceed if the user input is a subset of valid elements
                if set(user_input).issubset(valid_elems):

                    # Replace aliases with valid identifiers, if used
                    user_input = [group_dict[u] if u in valid_groups else u for
                                  u in user_input]

                    # Assign macro groups to nodes
                    macro_group(self.layout_graph, user_input)

                    continue

            # Check if the user has requested to delete a grouping node
            if 'rm' in user_input:

                # Get list of groups to delete
                user_input = user_input.lower().split()[1:]

                # Generate a dictionary of groups
                group_dict = get_node_dict(self.layout_graph, kind='group')

                # Count the current groups and enumerate for convenience. This
                # allows the user to refer to group number instead of complex
                # identifier.
                group_dict = {"g{}".format(i): k for i, (k, v) in
                              enumerate(group_dict.items(), start=1)}

                # Check for invalid input by comparing the user input and the
                # valid group identifiers as sets.
                while not set(user_input).issubset(set(group_dict.keys())):

                    # Get difference between user input and valid graph
                    diff = set(user_input).difference(set(group_dict.keys()))

                    # Print error message with difference in sets.
                    print("Sorry, {} is not a valid group identifier."
                          " Please try again.".format(' '.join(diff)))

                    # Break from the loop
                    break

                # Proceed if the user input is a subset of valid group ids
                if set(user_input).issubset(group_dict.keys()):

                    # Replace aliases with valid identifiers, if used
                    user_input = [group_dict[u] if u in group_dict.keys()
                                  else u for u in user_input]

                    # Update the graph according to user input
                    self.layout_graph.remove_nodes_from(user_input)

                    # Flag the graph for re-drawing
                    self.update = True

                    continue

            # If user input does not include a valid command, assume the input
            # is a string containing a list of diagram elements.
            elif user_input not in commands['generic']:

                # Split the input into a list
                user_input = user_input.split(',')

                # Strip extra whitespace
                user_input = [u.strip() for u in user_input]

                # Generate a list of valid diagram elements present in the graph
                valid_nodes = [e.lower() for e in self.layout_graph.nodes]

                # Generate a dictionary of groups
                group_dict = get_node_dict(self.layout_graph, kind='group')

                # Count the current groups and enumerate for convenience. This
                # allows the user to refer to group number instead of complex
                # identifier.
                group_dict = {"g{}".format(i): k for i, (k, v) in
                              enumerate(group_dict.items(), start=1)}

                # Create a list of identifiers based on the dict keys
                valid_groups = [g.lower() for g in group_dict.keys()]

                # Combine the valid nodes and groups into a set
                valid_elems = set(valid_nodes + valid_groups)

                # Check for invalid input by comparing the user input and the
                # valid elements as sets.
                if not set(user_input).issubset(valid_elems):

                    # Get difference between user input and valid element sets
                    diff = set(user_input).difference(valid_elems)

                    # Print error message with difference in sets
                    print("Sorry, {} is not a valid diagram element or command."
                          " Please try again.".format(' '.join(diff)))

                    continue

                # Proceed if the user input is a subset of valid elements
                if set(user_input).issubset(valid_elems):

                    # Check input length
                    if len(user_input) == 1:

                        # Print error message
                        print("Sorry, you must enter more than one identifier "
                              "to form a group.")

                        continue

                    # Proceed if aufficient number of valid elements is provided
                    elif len(user_input) > 1:

                        # Replace aliases with valid identifiers, if used
                        user_input = [group_dict[u] if u in valid_groups else
                                      u for u in user_input]

                        # Update the graph according to user input
                        group_nodes(self.layout_graph, user_input)

                        # Flag the graph for re-drawing
                        self.update = True

                # Continue until the annotation process is complete
                continue

    def annotate_connectivity(self):
        """
        A function for annotating a diagram for its connectivity.

        Parameters:
            None. The function populates the connectivity graph using the layout
            graph.

        Returns:
            Updated the graph contained in the Diagram object
            (self.connectivity_graph) according to the user input.
        """

        # Visualize the layout segmentation
        segmentation = draw_layout(self.image_path, self.annotation, 480)

        # Retrieve a list of valid nodes from the layout graph
        nodes = list(self.layout_graph.nodes(data=True))

        # Remove groups from the list of nodes
        nodes = [n for n in nodes if n[1]['kind'] != 'group']

        # Populate the connectivity graph according to the list of nodes
        self.connectivity_graph = create_graph(nodes,
                                               edges=False,
                                               arrowheads=False,
                                               mode='connect'
                                               )

        # Draw the graph using the layout mode
        diagram = draw_graph(self.connectivity_graph, dpi=100, mode='connect')

        # Set up flags for tracking whether annotation should be hidden or shown
        show = False
        hide = False

        # Enter a while loop for the annotation procedure
        while not self.connectivity_complete:

            # Check if the graph needs to be updated
            if self.update:

                # Re-draw the graph using the layout mode
                diagram = draw_graph(self.connectivity_graph, dpi=100,
                                     mode='connectivity')

                # Mark update complete
                self.update = False

            # Check if segmentation annotation is hidden and should be re-drawn
            if hide and show:

                # Visualize the layout segmentation
                segmentation = draw_layout(self.image_path, self.annotation,
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

                continue

            # Hide/show layout segmentation if requested
            if user_input == 'hide':

                # If hide is False, re-draw the layout without annotation
                if not hide:

                    # Re-draw the layout
                    segmentation = draw_layout(self.image_path,
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

                        # Check user input against nodes in graph; cast to set
                        valid_elems = set([e.lower() for e in
                                           self.connectivity_graph.nodes])

                        # Combine input for source and target nodes; cast to set
                        combined_input = set(source + target)

                        # Check for invalid input by comparing the user input
                        # with the set of valid elements.
                        if not combined_input.issubset(valid_elems):

                            # Get the difference in sets
                            diff = combined_input.difference(valid_elems)

                            # Print error message with difference in sets
                            print("Sorry, {} is not a valid diagram element. "
                                  "Please try again."
                                  .format(' '.join(diff)))

                            break

                        if combined_input.issubset(valid_elems):

                            # Set connection tracking flag to True
                            connection_found = True

                            continue

                # If a valid connection type is found, create a new connection
                if connection_found:

                    # Initialize a list for edge tuples
                    edge_bunch = []

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

    def annotate_rst(self):
        """
        A function for annotating the rhetorical structure (DPG-R) of a diagram.
        
        Parameters:
            None.
        
        Returns:
            Updates the RST graph in the Diagram object (self.rst_graph).
        """

        # Visualize the layout segmentation
        segmentation = draw_layout(self.image_path, self.annotation, 480)

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

        pass
