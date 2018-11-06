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

    # Save a screenshot if requested
    if user_input == 'cap':

        # Get filename of current image (without extension)
        fname = os.path.basename(diagram.image_path).split('.')[0]

        # Join filename to get a string
        fname = ''.join(fname)

        # Render high-resolution versions of graph and segmentation
        layout_hires = draw_layout(diagram.image_path,
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
    if user_input == 'comment':

        # Show a prompt for comment
        comment = input(prompts['comment'])

        # Return the comment
        diagram.comments.append(comment)

        return

    # If requested, mark the annotation as complete and remove isolates from the
    # graph.
    if user_input == 'done':

        # Find nodes without edges (isolates)
        isolates = list(nx.isolates(current_graph))

        # Remove isolates
        current_graph.remove_nodes_from(isolates)

        # Freeze the layout graph
        nx.freeze(current_graph)

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

        # Destroy any remaining windows
        cv2.destroyAllWindows()

        return

    # If requested, exit the annotator immediately
    if user_input == 'exit':

        exit("[INFO] Quitting ...")

    # Export a graphviz DOT graph if requested
    if user_input == 'export':

        # Get filename of current image (without extension)
        fname = os.path.basename(diagram.image_path).split('.')[0]

        # Join filename to get a string
        fname = ''.join(fname)

        # Write DOT graph to disk
        nx.nx_pydot.write_dot(current_graph,
                              '{}_{}.dot'.format(fname, mode))

        # Print status message
        print("[INFO] Saved a DOT graph for {}.png on disk.".format(fname))

        return

    # If requested, print info on current annotation task
    if user_input == 'info':

        # Clear screen first
        os.system('cls' if os.name == 'nt' else 'clear')

        # Print information on layout commands
        print(info[mode])
        print(info['generic'])

        return

    # If requested, remove isolates from the current graph
    if user_input == 'isolate':

        # Find nodes without edges (isolates)
        isolates = list(nx.isolates(current_graph))

        # Remove isolates
        current_graph.remove_nodes_from(isolates)

        # Print status message
        print("[INFO] Removing isolates as requested.")

        # Flag the graph for re-drawing
        diagram.update = True

        return

    # If requested, move to the next graph
    if user_input == 'next':

        # Destroy any remaining windows
        cv2.destroyAllWindows()

        return


# Define a dictionary of available commands during annotation
commands = {'rst': ['new', 'rels'],
            'layout': ['macrogroups'],
            'connectivity': [],
            'generic': ['cap', 'comment', 'done', 'exit', 'export', 'info',
                        'isolate', 'next']
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
                  "command 'macrogroups'."
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
                   "exit: Exit the annotator immediately.\n"
                   "export: Export the current graph into DOT format. \n"
                   "done: Mark the current diagram as complete and move on.\n"
                   "hide: Hide the annotation.\n"
                   "info: Print this message.\n"
                   "isolate: Remove isolates from the graph.\n"
                   "next: Move on to the next diagram.\n"
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
                 'iden': {'name': 'identification', 'kind': 'mono'},
                 'casc': {'name': 'class-ascription', 'kind': 'mono'},
                 'pasc': {'name': 'property-ascription', 'kind': 'mono'},
                 'poss': {'name': 'possession', 'kind': 'mono'},
                 'proj': {'name': 'projection', 'kind': 'mono'},
                 'effe': {'name': 'effect', 'kind': 'mono'},
                 'titl': {'name': 'title', 'kind': 'mono'}
                 }

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
