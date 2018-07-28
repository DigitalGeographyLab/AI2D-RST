# -*- coding: utf-8 -*-

import networkx as nx
import json


def create_graph(annotation, edges=False, arrowheads=False):
    """
    Draws an initial graph of diagram elements parsed from AI2D annotation.

    Parameters:
        annotation: A dictionary containing parsed AI2D annotation.
        edges: A boolean defining whether edges are to be drawn.
        arrowheads: A boolean defining whether arrowheads are drawn.

    Returns:
        A networkx graph with diagram elements.
    """
    # Check for correct input type
    assert isinstance(annotation, dict)

    # Parse the annotation from the dictionary
    diagram_elements, relations = parse_annotation(annotation)

    # Extract element types
    element_types = extract_types(diagram_elements, annotation)

    # Check if arrowheads should be excluded
    if not arrowheads:
        # Remove arrowheads from the dictionary
        element_types = {k: v for k, v in element_types.items()
                         if v != 'arrowHeads'}

    # Set up a dictionary to track arrows and arrowheads
    arrowmap = {}

    # Create a new graph
    graph = nx.Graph()

    # Add diagram elements to the graph and record their type (kind)
    for element, kind in element_types.items():
        graph.add_node(element, kind=kind)

    # Draw edges between nodes if requested
    if edges:

        # Loop over individual relations
        for relation, attributes in relations.items():

            # If the relation is 'arrowHeadTail', draw an edge between the
            # arrow and its head
            if attributes['category'] == 'arrowHeadTail':
                # Add edge to graph
                graph.add_edge(attributes['origin'],
                               attributes['destination'])

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

                        # Then draw an edge between arrowhead and
                        # destination, fetching the arrowhead identifier
                        # from the dictionary
                        graph.add_edge(arrowmap[attributes['connector']],
                                       attributes['destination'])

                    else:
                        # If the connector does not have an arrowhead, draw
                        # edge from origin to destination via the connector
                        graph.add_edge(attributes['origin'],
                                       attributes['connector'])

                        graph.add_edge(attributes['connector'],
                                       attributes['destination'])

            # If connector does not exist, draw a normal relation between
            # the origin and the destination
            except KeyError:
                graph.add_edge(attributes['origin'],
                               attributes['destination'])

    # Return graph
    return graph


def extract_types(elements, annotation):
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


def get_node_dict(graph, kind=None):
    """
    A function for creating a dictionary of nodes and their kind.

    Parameters:
        graph: A networkx graph.
        kind: A string defining what to include in the dictionary. 'node'
              returns only nodes and 'group' returns only groups. By
              default, the function returns all nodes defined in the graph.

    Returns:
        A dictionary with node names as keys and kind as values.
    """

    # Generate a dictionary with nodes and their kind
    node_types = nx.get_node_attributes(graph, 'kind')

    # If the requested output consists of node groups, return group dict
    if kind == 'group':
        # Generate a dictionary of groups
        group_dict = {k: k for k, v in node_types.items() if
                      v == 'group'}

        # Return dictionary
        return group_dict

    # If the requested output consists of nodes, return node dict
    if kind == 'node':

        # Generate a dictionary of nodes
        node_dict = {k: k for k, v in node_types.items() if v not in
                     ['group', 'relation']}

        # Return dictionary
        return node_dict

    # If the requested output consists of relations, return relation dict
    if kind == 'relation':

        # Generate a dictionary of RST relations
        rel_dict = {k: k for k, v in node_types.items() if v ==
                    'relation'}

        # Return dictionary
        return rel_dict

    # Otherwise return all node types
    else:
        return node_types


def load_annotation(json_path):
    """
    Loads AI2D annotation from a JSON file and returns the annotation as a
    dictionary.

    Parameters:
         json_path: A string containing the filepath to annotation.

    Returns:
         A dictionary containing AI2D annotation.
    """
    # Open the file containing the annotation
    with open(json_path) as annotation_file:

        # Parse the AI2D annotation from the JSON file into a dictionary
        annotation = json.load(annotation_file)

    # Return the annotation
    return annotation


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

    try:
        # Parse the diagram elements defined in the annotation, cast into list
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
