# -*- coding: utf-8 -*-

from .draw import *


def process_command(user_input, mode, diagram, current_graph):
    """
    A function for handling generic commands coming in from multiple annotation
    tasks.

    Parameters:
        user_input: A string containing the command entered by the user.
        mode: A string defining the current annotation task, either 'layout',
              'connectivity' or 'rst'.
        diagram: A Diagram class object that is currently being annotated.
        current_graph: The graph of a Diagram currently being annotated.

    Returns:
        Performs the requested action.
    """

    # Extract command from the user input
    command = user_input.split()[0]

    # Save a screenshot if requested
    if command == 'cap':

        # Get filename of current image (without extension)
        fname = os.path.basename(diagram.image_filename).split('.')[0]

        # Join filename to get a string
        fname = ''.join(fname)

        # Render high-resolution versions of graph and segmentation
        layout_hires = draw_layout(diagram.image_filename,
                                   diagram.annotation,
                                   height=720,
                                   dpi=200)

        diag_hires = draw_graph(current_graph, dpi=200,
                                mode=mode)

        # Write image on disk
        cv2.imwrite("segmentation_{}.png".format(fname), layout_hires)
        cv2.imwrite("{}_{}.png".format(mode, fname), diag_hires)

        # Print status message
        print("[INFO] Saved screenshots to disk for {}.png".format(
            fname
        ))

        return

    # Store a comment if requested
    if command == 'comment':

        # Show a prompt for comment
        comment = input(prompts['comment'])

        # Return the comment
        diagram.comments.append(comment)

        return

    # If requested, mark the annotation as complete and remove isolates from the
    # graph.
    if command == 'done':

        # Check the annotation task and mark complete as appropriate
        if mode == 'layout':

            # Set status to complete
            diagram.group_complete = True

            # Print status message
            print("[INFO] Marking grouping as complete.")

        if mode == 'connectivity':

            # Set status to complete
            diagram.connectivity_complete = True

            print("[INFO] Marking connectivity as complete.")

        if mode == 'rst':

            # Set status to complete
            diagram.rst_complete = True

            print("[INFO] Marking rhetorical structure as complete.")

        # Remove grouping edges from RST and connectivity annotation
        if mode == 'rst' or mode == 'connectivity':

            # Retrieve a list of edges in the graph
            edge_bunch = list(current_graph.edges(data=True))

            # Collect grouping edges from the edge list
            try:
                edge_bunch = [(u, v) for (u, v, d) in edge_bunch
                              if d['kind'] == 'grouping']

            except KeyError:
                pass

            # Remove grouping edges from current graph
            current_graph.remove_edges_from(edge_bunch)

        # Find nodes without edges (isolates)
        isolates = list(nx.isolates(current_graph))

        # Remove isolates
        current_graph.remove_nodes_from(isolates)

        # Freeze the graph
        nx.freeze(current_graph)

        # Destroy any remaining windows
        cv2.destroyAllWindows()

        return

    # If requested, exit the annotator immediately
    if command == 'exit':

        exit("[INFO] Quitting ...")

    # Export a graphviz DOT graph if requested
    if command == 'export':

        # Get filename of current image (without extension)
        fname = os.path.basename(diagram.image_filename).split('.')[0]

        # Join filename to get a string
        fname = ''.join(fname)

        # Remove grouping edges from RST and connectivity annotation
        if mode == 'rst' or mode == 'connectivity':

            # Retrieve a list of edges in the graph
            edge_bunch = list(current_graph.edges(data=True))

            # Collect grouping edges from the edge list
            try:
                edge_bunch = [(u, v) for (u, v, d) in edge_bunch
                              if d['kind'] == 'grouping']

            except KeyError:
                pass

            # Remove grouping edges from current graph
            current_graph.remove_edges_from(edge_bunch)

        # Find nodes without edges (isolates)
        isolates = list(nx.isolates(current_graph))

        # Remove isolates
        current_graph.remove_nodes_from(isolates)

        # Write DOT graph to disk
        nx.nx_pydot.write_dot(current_graph,
                              '{}_{}.dot'.format(fname, mode))

        # Print status message
        print("[INFO] Saved a DOT graph for {}.png on disk.".format(fname))

        return

    # If requested, release all connections leading to a node
    if command == 'free':

        # Prepare input for validation
        user_input = prepare_input(user_input, 1)

        # Check input against current graph
        valid = validate_input(user_input, current_graph)

        # If the input is not valid, return
        if not valid:

            return

        # If the input is valid, proceed
        if valid:

            # Generate a dictionary mapping group aliases to IDs
            group_dict = replace_aliases(diagram.layout_graph, 'group')

            # Replace aliases with valid identifiers, if used
            user_input = [group_dict[u] if u in group_dict.keys()
                          else u.upper() for u in user_input]

            # If mode is RST, replace aliases for relations as well
            if mode == 'rst':

                # Generate a dictionary mapping relation aliases to IDs
                rel_dict = replace_aliases(diagram.rst_graph, 'relation')

                # Replace aliases with valid identifiers, if used
                user_input = [rel_dict[u] if u in rel_dict.keys()
                              else u.upper() for u in user_input]

            # Retrieve the list of edges to delete
            edge_bunch = list(current_graph.edges(user_input))

            # Remove designated edges
            current_graph.remove_edges_from(edge_bunch)

            # Flag the graph for re-drawing
            diagram.update = True

    # If requested, print info on current annotation task
    if command == 'info':

        # Clear screen first
        os.system('cls' if os.name == 'nt' else 'clear')

        # Print information on layout commands
        print(info[mode])
        print(info['generic'])

        return

    # If requested, remove isolates from the current graph
    if command == 'isolate':

        # Find nodes without edges (isolates)
        isolates = list(nx.isolates(current_graph))

        # Remove isolates
        current_graph.remove_nodes_from(isolates)

        # Print status message
        print("[INFO] Removing isolates from the graph as requested.")

        # Flag the graph for re-drawing
        diagram.update = True

        return

    # If requested, print macro-groups
    if command == 'macrogroups':

        # Print header for available macro-groups
        print("---\nAvailable macro-groups and their aliases\n---")

        # Print the available macro-groups and their aliases
        for k, v in macro_groups.items():
            print("{} (alias: {})".format(v, k))

        # Print closing line
        print("---")

        # Get current macro-groups from the layout graph
        mgroups = dict(nx.get_node_attributes(diagram.layout_graph,
                                              'macro_group'))

        # If more than one macro-group has been defined, print groups
        if len(mgroups) > 0:

            # Print header for current macro-groups
            print("\nCurrent macro-groups \n---")

            # Print the currently defined macro-groups
            for k, v in mgroups.items():
                print("{}: {}".format(k, v))

            # Print closing line
            print("---\n")

        return

    # If requested, move to the next graph
    if command == 'next':

        # Destroy any remaining windows
        cv2.destroyAllWindows()

        return

    # If requested, removing grouping nodes
    if command == 'ungroup':

        # Retrieve a list of edges in the graph
        edge_bunch = list(current_graph.edges(data=True))

        # Collect grouping edges from the edge list
        edge_bunch = [(u, v) for (u, v, d) in edge_bunch
                      if d['kind'] == 'grouping']

        # Remove grouping edges from current graph
        current_graph.remove_edges_from(edge_bunch)

        # Flag the graph for re-drawing
        diagram.update = True

        return

    # If requested, print available RST relations
    if command == 'rels':

        # Clear screen first
        os.system('cls' if os.name == 'nt' else 'clear')

        # Print header for available macro-groups
        print("---\nAvailable RST relations and their aliases\n---")

        # Loop over RST relations
        for k, v in rst_relations.items():
            # Print information on each RST relation
            print("{} (alias: {}, type: {})".format(
                v['name'],
                k,
                v['kind']))

        # Print closing line
        print("---")

        # Generate a dictionary of RST relations present in the graph
        relation_ix = get_node_dict(current_graph, kind='relation')

        # Loop through current RST relations and rename for convenience.
        relation_ix = {"R{}".format(i): k for i, (k, v) in
                       enumerate(relation_ix.items(), start=1)}

        # If more than one macro-group has been defined, print groups
        if len(relation_ix) > 0:

            # Print header for current macro-groups
            print("\nCurrent RST relations \n---")

            # Print relations currently defined in the graph
            for k, v in relation_ix.items():

                print("{}: {}".format(k,
                                      diagram.rst_graph.nodes[v]['rel_name']))

            # Print closing line
            print("---\n")

        return

    # If requested, reset the annotation
    if command == 'reset':

        # Reset layout graph if requested
        if mode == 'layout':

            # Unfreeze the reset graph and assign to layout_graph
            diagram.layout_graph = diagram.reset.copy()

        # Reset connectivity graph if requested
        if mode == 'connectivity':

            # Unfreeze the connectivity graph and assign to connectivity_graph
            diagram.connectivity_graph = diagram.reset.copy()

        # Reset RST graph if requested
        if mode == 'rst':

            # Unfreeze the RST graph and assign to rst_graph
            diagram.rst_graph = diagram.reset.copy()

        # Flag the graph for re-drawing
        diagram.update = True

        return

    # If requested, delete grouping nodes
    if command == 'rm':

        # Prepare input for validation
        user_input = prepare_input(user_input, 1)

        # Check if RST relations need to be included in validation
        if mode == 'rst':

            # Validate input against relations as well
            valid = validate_input(user_input, current_graph, rst=True)

        else:
            # Check input against the current graph
            valid = validate_input(user_input, current_graph)

        # If the input is not valid, continue
        if not valid:

            return

        # If input is valid, proceed
        if valid:

            # Generate a dictionary mapping group aliases to IDs
            group_dict = replace_aliases(current_graph, 'group')

            # Replace aliases with valid identifiers, if used
            user_input = [group_dict[u] if u in group_dict.keys()
                          else u for u in user_input]

            # If annotating RST relations, check RST relations as well
            if mode == 'rst':

                # Generate a dictionary mapping relation aliases to IDs
                rel_dict = replace_aliases(current_graph, 'relation')

                # Replace aliases with valid identifiers, if used
                user_input = [rel_dict[u] if u in rel_dict.keys()
                              else u.upper() for u in user_input]

            # Remove the designated nodes from the graph
            current_graph.remove_nodes_from(user_input)

            # Flag the graph for re-drawing
            diagram.update = True

            return


# Define a dictionary of available commands during annotation
commands = {'rst': ['rels', 'ungroup'],
            # 'layout': ['macrogroups'],
            'connectivity': ['ungroup'],
            'generic': ['cap', 'comment', 'done', 'exit', 'export', 'free',
                        'info', 'isolate', 'macrogroups', 'next', 'reset', 'rm']
            }

info = {'layout': "---\n"
                  "Enter the identifiers of diagram elements you wish to group "
                  "together.\n"
                  "Separate the identifiers with a comma.\n"
                  "\n"
                  "Example of valid input: b1, a1, t1\n\n"
                  ""
                  "This command groups nodes B1, A1 and T1 together under a "
                  "grouping node.\n"
                  "---\n"
                  "Grouping nodes may be deleted using command rm.\n\n"
                  "Example command: rm g1\n\n"
                  "This command deletes group G1. Multiple groups can be\n"
                  "deleted by entering multiple identifiers, e.g. rm g1 g2 g3\n"
                  "---\n"
                  "To add macro-grouping information to a node, group, image "
                  "constant or their group, enter the command 'macro' followed "
                  "by the identifier or identifiers.\n\n"
                  "Example command: macro i0\n\n"
                  "A list of available macro-groups can be printed using the "
                  "command 'macrogroups'. This command will also print all "
                  "currently defined macro-groups."
                  "---\n",
        'rst': "---\n"
               "Enter the command 'new' to create a new RST relation.\n"
               "The tool will then ask you to enter a valid name for the "
               "relation.\n"
               "Names are entered by using abbreviations, which can be listed "
               "using the command 'relations'.\n\n"
               "The tool will infer the type of relation and ask you to enter "
               "either a nucleus and satellites or several nuclei.\n"
               "---\n",
        'connectivity': "---\n"
                        "Drawing a connection between nodes requires three "
                        "types of information: source, connection type and "
                        "target.\n\n"
                        "The sources and targets must be valid identifiers for "
                        "elements and groups or lists of valid identifiers "
                        "separated using commas.\n\n"
                        "Example command: t1 > b0, b1\n\n"
                        "The connection type must be one of the following "
                        "shorthand aliases:\n\n"
                        "- for undirected lines\n"
                        "> for unidirectional arrow\n"
                        "<> for bidirectional arrow\n"
                        "---\n",
        'generic': "Other valid commands include:\n\n"
                   "cap: Save a screen capture of the current visualisation.\n"
                   "comment: Enter a comment about current diagram.\n"
                   "free: Remove all edges leading to a node, e.g. free b0.\n"
                   "exit: Exit the annotator immediately.\n"
                   "export: Export the current graph into DOT format. \n"
                   "done: Mark the current diagram as complete and move on.\n"
                   "hide: Hide the annotation.\n"
                   "info: Print this message.\n"
                   "isolate: Remove isolates from the graph.\n"
                   "next: Save current work and move on to the next diagram.\n"
                   "reset: Reset the current annotation.\n" 
                   "---",
        }

# Define a dictionary of various prompts presented to user during annotation
prompts = {'nucleus_id': "[RST] Enter the identifier of nucleus: ",
           'satellite_id': "[RST] Enter the identifier(s) of satellite(s): ",
           'layout_default': "[GROUPING] Please enter nodes to group or a valid"
                             " command: ",
           'comment': "Enter comment: ",
           'rst_default': "[RST] Please enter a valid command: ",
           'rel_prompt': "[RST] Please enter relation name: ",
           'nuclei_id': "[RST] Enter the identifiers of the nuclei: ",
           'macro_group': "[GROUPING] Please enter macro group type: ",
           'conn_default': "[CONNECTIVITY] Please enter a connection or a valid"
                           " command: "
           }

# Define a dictionary of various error messages that may arise during annotation
messages = {'nucleus_err': "Sorry, a mononuclear relation cannot have more "
                           "than one nucleus. Please try again.",
            'nuclei_err': "Sorry, a multinuclear relation must have more than "
                          "one nucleus. Please try again."}


# Define a dictionary of RST relations / types and their aliases (keys)
rst_relations = {'anti': {'name': 'antithesis', 'kind': 'mono'},
                 'back': {'name': 'background', 'kind': 'mono'},
                 'circ': {'name': 'circumstance', 'kind': 'mono'},
                 'conc': {'name': 'concession', 'kind': 'mono'},
                 'cond': {'name': 'condition', 'kind': 'mono'},
                 'elab': {'name': 'elaboration', 'kind': 'mono'},
                 'enab': {'name': 'enablement', 'kind': 'mono'},
                 'eval': {'name': 'evaluation', 'kind': 'mono'},
                 'evid': {'name': 'evidence', 'kind': 'mono'},
                 'pret': {'name': 'interpretation', 'kind': 'mono'},
                 'just': {'name': 'justify', 'kind': 'mono'},
                 'mean': {'name': 'means', 'kind': 'mono'},
                 'moti': {'name': 'motivation', 'kind': 'mono'},
                 'nvoc': {'name': 'nonvolitional-cause', 'kind': 'mono'},
                 'nvor': {'name': 'nonvolitional-result', 'kind': 'mono'},
                 'otws': {'name': 'otherwise', 'kind': 'mono'},
                 'prep': {'name': 'preparation', 'kind': 'mono'},
                 'purp': {'name': 'purpose', 'kind': 'mono'},
                 'rest': {'name': 'restatement', 'kind': 'multi'},
                 'solu': {'name': 'solutionhood', 'kind': 'mono'},
                 'summ': {'name': 'summary', 'kind': 'mono'},
                 'unls': {'name': 'unless', 'kind': 'mono'},
                 'volc': {'name': 'volitional-cause', 'kind': 'mono'},
                 'volr': {'name': 'volitional-result', 'kind': 'mono'},
                 'cont': {'name': 'contrast', 'kind': 'multi'},
                 'join': {'name': 'joint', 'kind': 'multi'},
                 'list': {'name': 'list', 'kind': 'multi'},
                 'sequ': {'name': 'sequence', 'kind': 'multi'},
                 'cseq': {'name': 'cyclic sequence', 'kind': 'multi'},  # NEW
                 'iden': {'name': 'identification', 'kind': 'mono'},
                 'casc': {'name': 'class-ascription', 'kind': 'mono'},
                 'pasc': {'name': 'property-ascription', 'kind': 'mono'},
                 'poss': {'name': 'possession', 'kind': 'mono'},
                 'proj': {'name': 'projection', 'kind': 'mono'},
                 'conn': {'name': 'connected', 'kind': 'multi'},  # NEW!
                 'titl': {'name': 'title', 'kind': 'mono'}
                 }

# Define a dictionary of valid macro-groups and their aliases
macro_groups = {'table': 'table',
                'hor': 'horizontal',
                'ver': 'vertical',
                'net': 'network',
                'cycle': 'cycle',
                'slice': 'slice',
                'cut': 'cut-out',
                'exp': 'exploded',
                'photo': 'photograph',
                'ill': 'illustration',
                'diag': 'diagrammatic'
                }

# TODO Document RST relations

# TODO Add command 'status' which gives the annotation status of diagram
# TODO Add commands that allow switching between annotation types
