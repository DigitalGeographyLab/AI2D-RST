#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import json
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os


class Annotate:
    """
    This class holds various functions for processing and parsing AI2D
    annotation.
    """
    def __init__(self):
        pass

    @staticmethod
    def load_annotation(path_to_annotation):
        """
        Loads AI2D annotation from a JSON file and returns the annotation as a
        dictionary.

        Parameters:
             path_to_annotation: A string containing the filepath to annotation.

        Returns:
             A dictionary containing AI2D annotation.
        """
        # Open the file containing the annotation
        with open(path_to_annotation) as annotation_file:
            # Parse the AI2D annotation from the JSON file into a dictionary
            annotation = json.load(annotation_file)

        # Return the annotation
        return annotation

    @staticmethod
    def parse_annotation(annotation):
        """
        Parses AI2D annotation stored in a dictionary and prepares the
        annotation for drawing a graph.

        Parameters:
            annotation: A dictionary containing AI2D annotation.

        Returns:
            A dictionary for drawing a graph of the annotation.
        """
        # List types of diagram elements to be added to the graph
        targets = ['blobs', 'arrows', 'text', 'arrowHeads', 'containers',
                   'imageConsts']

        # Parse the diagram elements defined in the annotation, cast into list
        try:
            diagram_elements = [list(annotation[t].keys()) for t in targets]

            # Filter empty diagram types
            diagram_elements = list(filter(None, diagram_elements))

            # Flatten the resulting list
            diagram_elements = [i for sublist in diagram_elements
                                for i in sublist]

        except KeyError:
            pass

        # Parse the semantic relations defined in the annotation into a dict
        try:
            relations = annotation['relationships']

        except KeyError:
            pass

        return diagram_elements, relations

    @staticmethod
    def extract_element_type(elements, annotation):
        """
        Extracts the types of the identified diagram elements.

        Parameters:
            elements: A list of diagram elements.
            annotation: A dictionary of AI2D annotation.

        Returns:
             A dictionary with element types as keys and identifiers as values.
        """
        # Check for correct input type
        assert isinstance(elements, list)
        assert isinstance(annotation, dict)

        # Define the target categories for various diagram elements
        targets = ['arrowHeads', 'arrows', 'blobs', 'text', 'containers',
                   'imageConsts']

        # Create a dictionary for holding element types
        element_types = {}

        # Loop over the diagram elements
        for e in elements:
            try:
                # Search for matches in the target categories
                for t in targets:
                    # Get the identifiers for each element category
                    ids = [i for i in annotation[t].keys()]

                    # If the element is found among the identifiers, add the
                    # type to the dictionary
                    if e in ids:
                        element_types[e] = t

            # Skip if the category is not found
            except KeyError:
                continue

        # Return the element type dictionary
        return element_types


class Draw:
    """
    This class holds various functions for visualizing AI2D annotation.
    """
    def __init__(self):
        pass

    @staticmethod
    def convert_colour(colour):
        """
        Converts a matplotlib colour name to BGR for OpenCV.

        Parameters:
            colour: A valid matplotlib colour name.

        Returns:
            A BGR three tuple.
        """
        # Convert matplotlib colour name to normalized RGB
        colour = matplotlib.colors.to_rgb(colour)

        # Multiply by 255 and round
        colour = tuple(round(255 * x) for x in colour)

        # Reverse the tuple for OpenCV
        return tuple(reversed(colour))

    @staticmethod
    def draw_graph(annotation):
        """
        Draws a graph of the parsed diagram elements.

        Parameters:
            annotation: A dictionary containing AI2D annotation.

        Returns:
            An image showing the drawn graph.
        """
        # Check for correct input type
        assert isinstance(annotation, dict)

        # Parse the annotation from the dictionary
        diagram_elements, relations = Annotate.parse_annotation(annotation)

        # Extract element types
        element_types = Annotate.extract_element_type(diagram_elements,
                                                      annotation)

        # Create a new graph
        graph = nx.Graph()

        # Set up a dictionary to track arrows and arrowheads
        arrowmap = {}

        # Add diagram elements to the graph and record their type (kind)
        for element, kind in element_types.items():
            graph.add_node(element, kind=kind)

        # Loop over individual relations
        for relation, attributes in relations.items():

            # If the relation is 'arrowHeadTail', draw an edge between the arrow
            # and its head
            if attributes['category'] == 'arrowHeadTail':
                graph.add_edge(attributes['origin'], attributes['destination'])

                # Add arrowhead information to the dict for tracking arrows
                arrowmap[attributes['origin']] = attributes['destination']

            # Next, check if the relation includes a connector
            try:
                if attributes['connector']:

                    # Check if the connector (arrow) has an arrowhead
                    if attributes['connector'] in arrowmap.keys():

                        # First, draw an edge between origin and connector
                        graph.add_edge(attributes['origin'],
                                       attributes['connector'])

                        # Then draw an edge between arrowhead and destination,
                        # fetching the arrowhead identifier from the dictionary
                        graph.add_edge(arrowmap[attributes['connector']],
                                       attributes['destination'])

                    else:
                        # If the connector does not have an arrowhead, draw edge
                        # from origin to destination via the connector
                        graph.add_edge(attributes['origin'],
                                       attributes['connector'])

                        graph.add_edge(attributes['connector'],
                                       attributes['destination'])

            # If connector does not exist, draw a normal relation between the
            # origin and the destination
            except KeyError:
                graph.add_edge(attributes['origin'], attributes['destination'])

        # Generate a label dictionary by taking the node attributes and removing
        # relations
        node_types = nx.get_node_attributes(graph, 'kind')
        label_dict = {k: k for k, v in node_types.items()}

        # Set up the matplotlib Figure and Axis
        fig = plt.figure(dpi=100)
        ax = fig.add_subplot(1, 1, 1)

        # Initialize a spring layout for the graph
        pos = nx.spring_layout(graph)

        # Attempt to draw nodes for text elements
        try:
            texts = [k for k, v in element_types.items() if v == 'text']
            nx.draw_networkx_nodes(graph, pos, nodelist=texts, alpha=1,
                                   node_color='dodgerblue', ax=ax)
        except KeyError:
            pass

        # Attempt to draw nodes for blobs
        try:
            blobs = [k for k, v in element_types.items() if v == 'blobs']
            nx.draw_networkx_nodes(graph, pos, nodelist=blobs, alpha=1,
                                   node_color='orangered', ax=ax)
        except KeyError:
            pass

        # Attempt to draw nodes for arrowheads
        try:
            arrowhs = [k for k, v in element_types.items() if v == 'arrowHeads']
            nx.draw_networkx_nodes(graph, pos, nodelist=arrowhs, alpha=1,
                                   node_color='darkorange', ax=ax)
        except KeyError:
            pass

        # Attempt to draw nodes for arrows
        try:
            arrows = [k for k, v in element_types.items() if v == 'arrows']
            nx.draw_networkx_nodes(graph, pos, nodelist=arrows, alpha=1,
                                   node_color='peachpuff', ax=ax)
        except KeyError:
            pass

        try:
            constants = [k for k, v in element_types.items() if
                         v == 'imageConsts']
            nx.draw_networkx_nodes(graph, pos, nodelist=constants, alpha=1,
                                   node_color='palegoldenrod', ax=ax)
        except KeyError:
            pass

        # Draw edges between nodes
        nx.draw_networkx_edges(graph, pos, alpha=0.5, ax=ax)

        # Draw labels
        nx.draw_networkx_labels(graph, pos, font_size=10, labels=label_dict)

        # Remove margins from the graph and axes from the plot
        fig.tight_layout(pad=0)
        plt.axis('off')

        # Save figure to file, read the file using OpenCV and remove the file
        plt.savefig('temp.png')
        img = cv2.imread('temp.png')
        os.remove('temp.png')

        # Return image
        return img

    @staticmethod
    def draw_layout(path_to_image, annotation):

        # Load the diagram image and make a copy
        img = cv2.imread(path_to_image).copy()

        # Begin by trying to draw the blobs.
        try:
            for b in annotation['blobs']:
                # Get blob ID
                blob_id = annotation['blobs'][b]['id']

                # Assign the blob points into a variable and convert into numpy
                # array
                points = np.array(annotation['blobs'][b]['polygon'], np.int32)

                # Reshape the numpy array for drawing
                points = points.reshape((-1, 1, 2))

                # Compute center of the drawn element
                m = cv2.moments(points)
                x = int(m["m10"] / m["m00"])
                y = int(m["m01"] / m["m00"])

                # Draw the polygon. Note that points must be in brackets to
                # be drawn as lines; otherwise only points will appear.
                cv2.polylines(img, [points], isClosed=True, thickness=1,
                              lineType=cv2.LINE_AA,
                              color=Draw.convert_colour('orangered'))

                # Insert the identifier into the middle of the element
                cv2.putText(img, blob_id, (x - 10, y + 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.75, color=(0, 0, 0),
                            lineType=cv2.LINE_AA, thickness=2)

        # Skip if there are no blobs to draw
        except KeyError:
            pass

        # Next, attempt to draw text blocks
        try:
            for t in annotation['text']:
                # Get text id
                text_id = annotation['text'][t]['id']

                # Get the start and end points of the rectangle and cast
                # them into tuples for drawing.
                rect = annotation['text'][t]['rectangle']

                # Get start and end coordinates for the rectangle
                start, end = tuple(rect[0]), tuple(rect[1])

                # Get center of rectangle
                c = (round((start[0] + end[0]) / 2 - 10),
                     round((start[1] + end[1]) / 2 + 10))

                # Draw the rectangle
                cv2.rectangle(img, start, end, thickness=1,
                              lineType=cv2.LINE_AA,
                              color=Draw.convert_colour('dodgerblue'))

                # Insert the identifier into the middle of the element
                cv2.putText(img, text_id, c, cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.75, color=(0, 0, 0),
                            lineType=cv2.LINE_AA, thickness=2)

        # Skip if there are no text boxes to draw
        except KeyError:
            pass

        # Finally, attempt to draw any arrows
        try:
            for a in annotation['arrows']:
                # Get arrow id
                arrow_id = annotation['arrows'][a]['id']

                # Assign the points into a variable
                points = np.array(annotation['arrows'][a]['polygon'], np.int32)

                # Reshape the numpy array for drawing
                points = points.reshape((-1, 1, 2))

                # Compute center of the drawn element
                m = cv2.moments(points)
                x = int(m["m10"] / m["m00"])
                y = int(m["m01"] / m["m00"])

                # Draw the polygon. Note that points must be in brackets to
                # be drawn as lines; otherwise only points will appear.
                cv2.polylines(img, [points], isClosed=True, thickness=1,
                              lineType=cv2.LINE_AA,
                              color=Draw.convert_colour('peachpuff'))

                # Insert the identifier into the middle of the element
                cv2.putText(img, arrow_id, (x - 10, y + 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.75, color=(0, 0, 0),
                            lineType=cv2.LINE_AA, thickness=2)

        # Skip if there are no arrows to draw
        except KeyError:
            pass

        # Calculate aspect ratio (target width / current width) and new
        # width of the preview image.
        (h, w) = img.shape[:2]
        r = 480 / h
        dim = (int(w * r), 480)

        # Resize the preview image
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

        return img
