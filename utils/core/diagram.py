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
    def __init__(self, json, image):
        """
        This function initializes the Diagram class.
        
        Parameters:
            json: Path to the JSON file containing the original AI2D annotation 
                  or a dictionary containing parsed annotation.
            image: Path to the image file containing the diagram.
            
        Returns:
            An AI2D Diagram object with various methods and attributes.
        """
        # Mark the annotation initially as not complete
        self.complete = False
        self.rst_complete = False
        self.layout_complete = False

        # Set image path
        self.image_path = image

        # Continue by checking the annotation type. If the input is a dictionary
        # assign the dictionary to the variable 'annotation'.
        if type(json) == dict:
            self.annotation = json

        else:
            # Load JSON annotation into a dictionary
            self.annotation = load_annotation(json)

        # Create initial graph with diagram elements only
        self.layout_graph = create_graph(self.annotation,
                                         edges=False,
                                         arrowheads=False,
                                         mode='layout'
                                         )

        # Create a graph for RST annotation
        self.rst_graph = create_graph(self.annotation,
                                      edges=False,
                                      arrowheads=False,
                                      mode='rst'
                                      )

        # Visualise the layout annotation in an image
        self.layout = draw_layout(self.image_path, self.annotation, 480)

        # Set up placeholders for the layout graph and comments
        self.comments = []

    def annotate_layout(self):
        """
        A function for annotating the logical / layout structure (DPG-L) of a
        diagram.
        
        Parameters:
            None. The function modifies the graph that is created when a Diagram
            object is initialised.
        
        Returns:
            Updates the graph contained in the Diagram object (self.graph)
            according to the user input.
        """

        # Enter a while loop for the annotation procedure
        while not self.layout_complete:

            # Draw the graph
            diagram = draw_graph(self.layout_graph, dpi=100)

            # Join the graph and the layout structure horizontally
            preview = np.hstack((diagram, self.layout))

            # Show the resulting visualization
            cv2.imshow("Annotation", preview)

            # Prompt user for input
            user_input = input(prompts['layout_default'])

            # Check if the input is a command
            if user_input in commands['layout']:

                # Quit the program immediately upon command
                if user_input == 'exit':

                    exit("Quitting ...")

                # If next diagram is requested, store current graph and move on
                if user_input == 'next':

                    # Destroy any remaining windows
                    cv2.destroyAllWindows()

                    return

                # Print information if requested
                if user_input == 'info':

                    # Clear screen first
                    os.system('cls' if os.name == 'nt' else 'clear')

                    # Print information on layout commands
                    print(info['layout'])

                    pass

                # Store a comment if requested
                if user_input == 'comment':

                    # Show a prompt for comment
                    comment = input(prompts['comment'])

                    # Return the comment
                    self.comments.append(comment)

                # If the user marks the annotation as complete
                if user_input == 'done':

                    # Set status to complete
                    self.layout_complete = True

                    # Destroy any remaining windows
                    cv2.destroyAllWindows()

                    return

                # Save a screenshot if requested
                if user_input == 'cap':

                    # Get filename of current image
                    fname = os.path.basename(self.image_path)

                    # Write image on disk
                    cv2.imwrite("screen_capture_{}.png".format(fname), preview)

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

                    continue

            # If user input does not include a valid command, assume the input
            # is a string containing a list of diagram elements.
            elif user_input not in commands['layout']:

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
                while not set(user_input).issubset(valid_elems):

                    # Get difference between user input and valid element sets
                    diff = set(user_input).difference(valid_elems)

                    # Print error message with difference in sets.
                    print("Sorry, {} is not a valid diagram element or command."
                          " Please try again.".format(' '.join(diff)))

                    # Break from the loop
                    break

                # Proceed if the user input is a subset of valid elements
                if set(user_input).issubset(valid_elems):

                    # Replace aliases with valid identifiers, if used
                    user_input = [group_dict[u] if u in valid_groups else u for
                                  u in user_input]

                    # Update the graph according to user input
                    group_nodes(self.layout_graph, user_input)

                # Continue until the annotation process is complete
                continue

    def annotate_rst(self):
        """
        A function for annotating the rhetorical structure (DPG-R) of a diagram.
        
        Parameters:
            None.
        
        Returns:
            Updates the RST graph in the Diagram object (self.rst_graph).
        """

        # Check if an RST graph is complete: use a non-method flag for now
        self.rst_complete = False

        # Enter a while loop for the annotation procedure
        while not self.rst_complete:

            # Draw the graph using RST mode
            diagram = draw_graph(self.rst_graph, dpi=100, mode='rst')

            # Join the graph and the layout structure horizontally
            preview = np.hstack((diagram, self.layout))

            # Show the resulting visualization
            cv2.imshow("Annotation", preview)

            # Prompt user for input
            user_input = input(prompts['rst_default'])

            # Check the input
            if user_input in commands['rst']:

                # Quit the program immediately upon command
                if user_input == 'exit':
                    exit("Quitting ...")

                # If next diagram is requested, store current graph and move on
                if user_input == 'next':

                    # Destroy any remaining windows
                    cv2.destroyAllWindows()

                    return

                # If the user marks the annotation as complete, change status
                if user_input == 'done':

                    # Set status to complete
                    self.rst_complete = True

                    # Destroy any remaining windows
                    cv2.destroyAllWindows()

                    return

                # If the user requests a list of available RST relations, print
                # the keys and their definitions.
                if user_input == 'relations':

                    # Clear screen first
                    os.system('cls' if os.name == 'nt' else 'clear')

                    # Loop over RST relations
                    for k, v in rst_relations.items():

                        # Print information on each RST relation
                        print("{} - abbreviation: {}, type: {}.".format(
                            v['name'].upper(),
                            k,
                            v['kind']))

                    pass

                # Print information if requested
                if user_input == 'info':

                    # Clear screen first
                    os.system('cls' if os.name == 'nt' else 'clear')

                    # Print information on layout commands
                    print(info['rst'])

                    pass

                # Store a comment if requested
                if user_input == 'comment':

                    # Show a prompt for comment
                    comment = input(prompts['comment'])

                    # Return the comment
                    self.comments.append(comment)

                # Save a screenshot if requested
                if user_input == 'cap':

                    # Get filename of current image
                    fname = os.path.basename(self.image_path)

                    # Write image on disk
                    cv2.imwrite("screen_capture_{}.png".format(fname), preview)

                # If the user marks the annotation as complete
                if user_input == 'done':

                    # Set status to complete
                    self.rst_complete = True

                    # Destroy any remaining windows
                    cv2.destroyAllWindows()

                    return

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

                    else:
                        print("Sorry, {} is not a valid relation."
                              .format(relation))

            if user_input not in commands['rst']:

                # Print error message
                print("Sorry, {} is not a valid command.".format(user_input))

                continue

        pass
