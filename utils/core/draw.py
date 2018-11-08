# -*- coding: utf-8 -*-

from .parse import *

import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import networkx as nx
import os


def draw_graph(graph, dpi=100, mode='layout'):
    """
    Draws an image of a NetworkX Graph for visual inspection.
    
    Parameters:
        graph: A NetworkX Graph.
        dpi: The resolution of the image as dots per inch.
        mode: String indicating the diagram structure to be drawn, valid options
              include 'layout' (default), 'connectivity' and 'rst'.
        
    Returns:
         An image showing the NetworkX Graph.
    """

    # Set up the matplotlib Figure, its resolution and Axis
    fig = plt.figure(dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)

    # Initialize a neato layout for the graph
    pos = nx.nx_pydot.graphviz_layout(graph, prog='neato')

    # Generate a dictionary with nodes and their kind
    node_types = nx.get_node_attributes(graph, 'kind')

    # Create a label dictionary for nodes
    node_dict = get_node_dict(graph, kind='node')

    # Check the mode, that is, which aspect of diagram structure is annotated
    if mode == 'layout' or mode == 'connectivity':

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
        rel_dict = {k: "R{} ({})".format(i, graph.node[k]['rel_name'])
                    for i, (k, v) in enumerate(rel_dict.items(), start=1)}

        # Get a dictionary of edge labels
        edge_dict = nx.get_edge_attributes(graph, 'kind')

        # TODO Find out why IO appears after defining a relation

    # Draw nodes present in the graph
    draw_nodes(graph, pos=pos, ax=ax, node_types=node_types, mode=mode)

    # Draw labels for each node in the graph
    nx.draw_networkx_labels(graph, pos, font_size=10, labels=node_dict)

    # Check the annotation mode before drawing labels for groups or relations
    if mode == 'layout' or mode == 'connectivity':

        # Draw labels for groups
        nx.draw_networkx_labels(graph, pos, font_size=10, labels=group_dict)

    if mode == 'rst':

        # Draw identifiers for RST relations
        nx.draw_networkx_labels(graph, pos, font_size=10, labels=rel_dict)

        # Draw edge labels for nuclei and satellites
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_dict)

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


def draw_layout(path_to_image, annotation, height, hide=False, **kwargs):
    """
    Visualizes the AI2D layout annotation on the original input image.

    Parameters:
        path_to_image: Path to the original AI2D diagram image.
        annotation: A dictionary containing AI2D annotation.
        height: Target height of the image.
        hide: A Boolean indicating whether to draw annotation or not.

    Returns:
        An image with the AI2D annotation overlaid.
    """

    # Load the diagram image and make a copy
    img, r = resize_img(path_to_image, height)

    # Change from BGR to RGB colourspace
    img = img[:, :, ::-1]

    # Create a matplotlib Figure
    fig, ax = plt.subplots(1)
    plt.tight_layout(pad=0)

    # Add the image to the axis
    ax.imshow(img)

    # Hide grid and axes
    plt.axis('off')

    # Check if the annotation should be hidden
    if hide:

        # Save figure to file, read the file using OpenCV and remove the file
        plt.savefig('temp.png')
        img = cv2.imread('temp.png')
        os.remove('temp.png')

        return img

    # Draw blobs
    try:
        for b in annotation['blobs']:

            # Get blob ID
            blob_id = annotation['blobs'][b]['id']

            # Assign the blob points into a variable and convert into numpy
            # array
            points = np.array(annotation['blobs'][b]['polygon'], np.int32)

            # Scale the coordinates according to the ratio; convert to int
            points = np.round(points * r, decimals=0).astype('int')

            # Creat arrow polygon
            blob = patches.Polygon(points,
                                   closed=True,
                                   fill=False,
                                   alpha=1,
                                   color='orangered')

            # Add arrow to the image
            ax.add_patch(blob)

            # Add artist for patch
            ax.add_artist(blob)

            # Get centroid
            cx, cy = np.round(points.mean(axis=0), decimals=0).astype('int')[:2]

            # Annotate the blob
            ann = ax.annotate(blob_id, (cx, cy), color='white',
                              fontsize=10, ha='center', va='center')

            # Add a box around the annotation
            ann.set_bbox(dict(alpha=1, color='orangered', pad=0))

    # Skip if there are no blobs to draw
    except KeyError:
        pass

    # Draw arrows
    try:
        for a in annotation['arrows']:

            # Get arrow ID
            arrow_id = annotation['arrows'][a]['id']

            # Assign the points into a variable
            points = np.array(annotation['arrows'][a]['polygon'], np.int32)

            # Scale the coordinates according to the ratio; convert to int
            points = np.round(points * r, decimals=0).astype('int')

            # Create an arrow polygon
            arrow = patches.Polygon(points,
                                    closed=True,
                                    fill=False,
                                    alpha=1,
                                    color='mediumseagreen')

            # Add arrow to the image
            ax.add_patch(arrow)

            # Add artist for patch
            ax.add_artist(arrow)

            # Get centroid
            cx, cy = np.round(points.mean(axis=0), decimals=0).astype('int')[:2]

            # Annotate the arrow
            ann = ax.annotate(arrow_id, (cx, cy), color='white', fontsize=10,
                              ha='center', va='center')

            # Add a box around the annotation
            ann.set_bbox(dict(alpha=1, color='mediumseagreen', pad=0))

    # Skip if there are no arrows to draw
    except KeyError:
        pass

    # Draw text blocks
    try:
        for t in annotation['text']:

            # Get text ID
            text_id = annotation['text'][t]['id']

            # Get the start and end points of the rectangle and cast
            # them into tuples for drawing.
            rect = np.array(annotation['text'][t]['rectangle'], np.int32)

            # Get start and end coordinates, convert to int and cast into tuple
            startx, starty = np.round(rect[0] * r, decimals=0).astype('int')
            endx, endy = np.round(rect[1] * r, decimals=0).astype('int')

            # Calculate bounding box width and height
            width = endx - startx
            height = endy - starty

            # Define a rectangle and add to batch
            rectangle = patches.Rectangle((startx, starty),
                                          width, height,
                                          fill=False,
                                          alpha=1,
                                          color='dodgerblue',
                                          edgecolor=None)

            # Add patch to the image
            ax.add_patch(rectangle)

            # Add artist object for rectangle
            ax.add_artist(rectangle)

            # Get starting coordinates
            x, y = rectangle.get_xy()

            # Get coordinates for the centre; adjust positioning
            cx = (x + rectangle.get_width() / 2.0)
            cy = (y + rectangle.get_height() / 2.0)

            # Add annotation to the text box
            ann = ax.annotate(text_id, (cx, cy), color='white',
                              fontsize=10, ha='center', va='center')

            # Add a box around the annotation
            ann.set_bbox(dict(alpha=1, color='dodgerblue', pad=0))

    # Skip if there are no text boxes to draw
    except KeyError:
        pass

    # Check if a high-resolution image has been requested
    if kwargs and 'dpi' in kwargs:

        # Save figure to file in the requested resolution
        plt.savefig('temp.png', dpi=kwargs['dpi'])

        img = cv2.imread('temp.png')
        os.remove('temp.png')

        return img

    # Save figure to file, read the file using OpenCV and remove the file
    plt.savefig('temp.png')
    img = cv2.imread('temp.png')
    os.remove('temp.png')

    # TODO Remove OpenCV dependency

    # Close the plot
    plt.close()

    # Return the annotated image
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
             'layout' (default), 'connectivity' and 'rst'.

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

    # Check drawing mode, start with layout
    if mode == 'layout' or mode == 'connectivity':

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
                                   ax=ax
                                   )

        # Skip if there are no group nodes to draw
        except KeyError:
            pass

    # Check drawing mode, continue with RST
    if mode == 'rst' and draw_edges:

        # Draw nodes for RST relations
        try:
            relations = [k for k, v in node_types.items() if v == 'relation']

            # Add the relations to the graph
            nx.draw_networkx_nodes(graph,
                                   pos,
                                   nodelist=relations,
                                   alpha=1,
                                   node_color='white',
                                   ax=ax
                                   )

        # Skip if there are no relations to draw
        except KeyError:
            pass

        # Get edge list
        edge_list = graph.edges(data=True)

        # Filter the edge list for satellite edges
        satellites = [(u, v, d) for (u, v, d) in edge_list
                      if d['kind'] == 'satellite']

        # Draw edges for satellites without arrows
        nx.draw_networkx_edges(graph,
                               pos,
                               satellites,
                               alpha=0.75,
                               arrows=False,
                               ax=ax)

        # Filter the edge list for nuclei edges
        nuclei = [(u, v, d) for (u, v, d) in edge_list
                  if d['kind'] == 'nucleus']

        # Draw edges for nuclei with arrows
        nx.draw_networkx_edges(graph,
                               pos,
                               nuclei,
                               alpha=0.75,
                               arrows=True,
                               ax=ax)

    # Check drawing mode, finish with connectivity
    if mode == 'connectivity' and draw_edges:

        # Get a list of all edges
        all_edges = list(graph.edges(data=True))

        # Draw undirectional edges
        try:

            # Filter the edges, retaining only undirectional edges
            undirectional = [(u, v, d) for u, v, d in all_edges
                             if d['kind'] == 'undirectional']

            # Draw edges without arrows
            nx.draw_networkx_edges(graph,
                                   pos,
                                   undirectional,
                                   alpha=0.75,
                                   arrows=False,
                                   ax=ax
                                   )

        # Skip if no undirectional arrows are found
        except KeyError:

            pass

        # Draw other edges
        try:

            # Filter the edges, retaining only directional/bidirectional edges
            directional = [(u, v, d) for (u, v, d) in all_edges
                           if d['kind'] in ['directional', 'bidirectional']]

            # Draw edges with arrows
            nx.draw_networkx_edges(graph,
                                   pos,
                                   directional,
                                   alpha=0.75,
                                   arrows=True,
                                   ax=ax
                                   )

        # Skip if no directional/bidirectional edges are found
        except KeyError:

            pass

        # Draw grouping edges
        try:
            # Fetch a list of grouping edges (which do not have any attributes!)
            grouping_edges = [(u, v, d) for (u, v, d) in all_edges if
                              d['kind'] == 'grouping']

            # Draw edges between elements and their grouping nodes
            nx.draw_networkx_edges(graph,
                                   pos,
                                   grouping_edges,
                                   alpha=0.5,
                                   style='dotted',
                                   arrows=False,
                                   ax=ax)

        # Skip if no grouping edges are found
        except KeyError:

            pass

    # Otherwise, draw standard edges if requested
    if draw_edges and mode == 'layout':

        # Draw edges between nodes
        nx.draw_networkx_edges(graph,
                               pos,
                               alpha=0.75,
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
