# -*- coding: utf-8 -*-

from .parse import *

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import os


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


def draw_graph(graph, dpi=100, mode='layout'):
    """
    Draws an image of a NetworkX Graph for visual inspection.
    
    Parameters:
        graph: A NetworkX Graph.
        dpi: The resolution of the image as dots per inch.
        mode: String indicating the diagram structure to be drawn, valid options
              include 'layout' and 'rst'. Default mode is layout.
        
    Returns:
         An image showing the NetworkX Graph.
    """

    # Set up the matplotlib Figure, its resolution and Axis
    fig = plt.figure(dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)

    # Initialize a spring layout for the graph
    pos = nx.spring_layout(graph, iterations=20)

    # Generate a dictionary with nodes and their kind
    node_types = nx.get_node_attributes(graph, 'kind')

    # Create a label dictionary for nodes
    node_dict = get_node_dict(graph, kind='node')

    # Check the mode, that is, whether the Graph represents the layout/logical
    # or RST structure
    if mode == 'layout':

        # Create a label dictionary for grouping nodes
        group_dict = get_node_dict(graph, kind='group')

        # Enumerate groups and use their numbers as labels for clarity
        group_dict = {k: "G{}".format(i) for i, (k, v) in
                      enumerate(group_dict.items(), start=1)}

    if mode == 'rst':

        # Create a label dictionary for RST relations
        rel_dict = get_node_dict(graph, kind='relation')

        # Enumerate relations and use their numbers as labels for clarity; add
        # relation name to the label by fetching it from the graph.
        rel_dict = {k: "R{} ({})".format(i, graph.node[k]['name']) for i, (k, v)
                    in enumerate(rel_dict.items(), start=1)}

    # Draw nodes
    draw_nodes(graph, pos=pos, ax=ax, node_types=node_types, mode=mode)

    # Draw labels for nodes
    nx.draw_networkx_labels(graph, pos, font_size=10,
                            labels=node_dict)

    # Check the mode
    if mode == 'layout':

        # Draw labels for groups
        nx.draw_networkx_labels(graph, pos, font_size=10,
                                labels=group_dict)

    if mode == 'rst':

        # Draw labels for RST relations
        nx.draw_networkx_labels(graph, pos, font_size=10,
                                labels=rel_dict)

    # Remove margins from the graph and axes from the plot
    fig.tight_layout(pad=0)
    plt.axis('off')

    # Save figure to file, read the file using OpenCV and remove the file
    plt.savefig('temp.png')
    img = cv2.imread('temp.png')
    os.remove('temp.png')

    # Close matplotlib figure
    plt.close()

    return img


def draw_layout(path_to_image, annotation, height):
    """
    Visualizes the AI2D layout annotation on the original input image.

    Parameters:
        path_to_image: Path to the original AI2D diagram image.
        annotation: A dictionary containing AI2D annotation.
        height: Target height of the image.

    Returns:
        An image with the AI2D annotation overlaid.
    """

    # Load the diagram image and make a copy
    img, r = resize_img(path_to_image, height)

    # Begin drawing the blobs.
    try:
        for b in annotation['blobs']:

            # Get blob ID
            blob_id = annotation['blobs'][b]['id']

            # Assign the blob points into a variable and convert into numpy
            # array
            points = np.array(annotation['blobs'][b]['polygon'], np.int32)

            # Scale the coordinates according to the ratio; convert to int
            points = np.round(points * r, decimals=0).astype('int')

            # Reshape the numpy array for drawing
            points = points.reshape((-1, 1, 2))

            # Get moment values
            m = cv2.moments(points)

            # Calculate centroid of the polygon; catch errors arising from
            # elements that are positioned in coordinates (0, 0).
            try:
                x = int(m["m10"] / m["m00"])
            except ZeroDivisionError:
                pass

            try:
                y = int(m["m01"] / m["m00"])
            except ZeroDivisionError:
                pass

            # Draw the polygon. Note that points must be in brackets to
            # be drawn as lines; otherwise only points will appear.
            cv2.polylines(img, [points], isClosed=True, thickness=2,
                          lineType=cv2.LINE_AA,
                          color=convert_colour('orangered'))

            # Insert the identifier into the middle of the element
            cv2.putText(img, blob_id, (x - 10, y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, lineType=cv2.LINE_AA, thickness=1,
                        color=convert_colour('magenta'))

    # Skip if there are no blobs to draw
    except KeyError:
        pass

    # Next, draw text blocks
    try:
        for t in annotation['text']:
            # Get text ID
            text_id = annotation['text'][t]['id']

            # Get the start and end points of the rectangle and cast
            # them into tuples for drawing.
            rect = annotation['text'][t]['rectangle']

            # Scale the coordinates according to the ratio; convert to int
            rect[0] = [np.round(x * r, decimals=0).astype('int')
                       for x in rect[0]]
            rect[1] = [np.round(x * r, decimals=0).astype('int')
                       for x in rect[1]]

            # Get start and end coordinates for the rectangle
            start, end = tuple(rect[0]), tuple(rect[1])

            # Get center of rectangle; cast into integer
            c = (round((start[0] + end[0]) / 2 - 10).astype('int'),
                 round((start[1] + end[1]) / 2 + 10).astype('int'))

            # Draw the rectangle
            cv2.rectangle(img, start, end, thickness=2,
                          lineType=cv2.LINE_AA,
                          color=convert_colour('dodgerblue'))

            # Insert the identifier into the middle of the element
            cv2.putText(img, text_id, c, cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, lineType=cv2.LINE_AA, thickness=1,
                        color=convert_colour('magenta'))

    # Skip if there are no text boxes to draw
    except KeyError:
        pass

    # Finally, draw any arrows
    try:
        for a in annotation['arrows']:
            # Get arrow ID
            arrow_id = annotation['arrows'][a]['id']

            # Assign the points into a variable
            points = np.array(annotation['arrows'][a]['polygon'], np.int32)

            # Scale the coordinates according to the ratio; convert to int
            points = np.round(points * r, decimals=0).astype('int')

            # Reshape the numpy array for drawing
            points = points.reshape((-1, 1, 2))

            # Compute center of the drawn element
            m = cv2.moments(points)
            x = int(m["m10"] / m["m00"])
            y = int(m["m01"] / m["m00"])

            # Draw the polygon. Note that points must be in brackets to
            # be drawn as lines; otherwise only points will appear.
            cv2.polylines(img, [points], isClosed=True, thickness=2,
                          lineType=cv2.LINE_AA,
                          color=convert_colour('mediumseagreen'))

            # Insert the identifier into the middle of the element
            cv2.putText(img, arrow_id, (x - 10, y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=convert_colour('magenta'),
                        lineType=cv2.LINE_AA, thickness=1)

    # Skip if there are no arrows to draw
    except KeyError:
        pass

    # Return image
    return img


def draw_nodes(graph, pos, ax, node_types, draw_edges=True, mode='layout'):
    """
    A generic function for visualising the nodes in a graph.

    Parameters:
        graph: A NetworkX Graph.
        pos: Positions for the NetworkX Graph.
        ax: Matplotlib Figure Axis on which to draw.
        node_types: A dictionary of node types extracted from the Graph.
        draw_edges: A boolean indicating whether edges should be drawn.
        mode: A string indicating the selected drawing mode. Valid options are
             'layout' (default) and 'rst'.

    Returns:
         None
    """

    # Draw nodes for text elements
    try:
        # Retrieve text nodes for the list of nodes
        texts = [k for k, v in node_types.items() if v == 'text']

        # Add the list of nodes to the graph
        nx.draw_networkx_nodes(graph,
                               pos,
                               nodelist=texts,
                               alpha=1,
                               node_color='dodgerblue',
                               ax=ax
                               )

    # Skip if there are no text nodes to draw
    except KeyError:
        pass

    # Draw nodes for blobs
    try:
        # Retrieve blob nodes for the list of nodes
        blobs = [k for k, v in node_types.items() if v == 'blobs']

        # Add the list of nodes to the graph
        nx.draw_networkx_nodes(graph,
                               pos,
                               nodelist=blobs,
                               alpha=1,
                               node_color='orangered',
                               ax=ax
                               )

    # Skip if there are no blob nodes to draw
    except KeyError:
        pass

    # Draw nodes for arrowheads
    try:
        # Retrieve arrowhead nodes for the list of nodes
        arrowhs = [k for k, v in node_types.items() if v == 'arrowHeads']

        # Add the list of arrowheads to the graph
        nx.draw_networkx_nodes(graph,
                               pos,
                               nodelist=arrowhs,
                               alpha=1,
                               node_color='darkorange',
                               ax=ax
                               )

    # Skip if there are no arrowheads to draw
    except KeyError:
        pass

    # Draw nodes for arrows
    try:
        # Retrieve arrow nodes for the list of nodes
        arrows = [k for k, v in node_types.items() if v == 'arrows']

        # Add the list of arrows to the graph
        nx.draw_networkx_nodes(graph,
                               pos,
                               nodelist=arrows,
                               alpha=1,
                               node_color='mediumseagreen',
                               ax=ax
                               )

    # Skip if there are no arrows to draw
    except KeyError:
        pass

    # Check drawing mode
    if mode == 'layout':

        # Draw nodes for imageConsts
        try:
            # Retrieve image constants (in most cases, only one per diagram)
            constants = [k for k, v in node_types.items() if
                         v == 'imageConsts']

            # Add the image constants to the graph
            nx.draw_networkx_nodes(graph,
                                   pos,
                                   nodelist=constants,
                                   alpha=1,
                                   node_color='palegoldenrod',
                                   ax=ax
                                   )

        # Skip if there are no image constants to draw
        except KeyError:
            pass

        # Draw nodes for element groups
        try:
            # Retrieve the group nodes for the list of nodes
            groups = [k for k, v in node_types.items() if v == 'group']

            # Add the group nodes to the graph
            nx.draw_networkx_nodes(graph,
                                   pos,
                                   nodelist=groups,
                                   alpha=1,
                                   node_color='navajowhite',
                                   ax=ax,
                                   node_size=50
                                   )

        # Skip if there are no group nodes to draw
        except KeyError:
            pass

    if mode == 'rst':

        # Draw nodes for relations
        try:
            relations = [k for k, v in node_types.items() if v == 'relation']

            # Add the relations to the graph
            nx.draw_networkx_nodes(graph,
                                   pos,
                                   nodelist=relations,
                                   alpha=1,
                                   node_color='white',
                                   ax=ax,
                                   node_size=25
                                   )

        # Skip if there are no relations to draw
        except KeyError:
            pass

    # Draw edges if requested
    if draw_edges:

        # Draw edges between nodes
        nx.draw_networkx_edges(graph,
                               pos,
                               alpha=0.5,
                               ax=ax
                               )


def resize_img(path_to_image, height):
    """
    Resizes an image.

    Parameters:
        path_to_image: Path to the image to resize.
        height: Requested height of the resized image.

    Returns:
        The resized image and the ratio used for resizing.
    """

    # Load the diagram image and make a copy
    img = cv2.imread(path_to_image).copy()

    # Calculate aspect ratio (target width / current width) and new
    # width of the preview image.
    (h, w) = img.shape[:2]

    # Calculate ratio based on image height
    r = height / h
    dim = (int(w * r), height)

    # Resize the preview image
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    # Return image
    return img, r
