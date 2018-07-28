# -*- coding: utf-8 -*-

# Define a dictionary of available commands during annotation
commands = {'rst': ['info', 'define', 'next', 'exit', 'done', 'cap', 'new',
                    'comment', 'rels'],
            'layout': ['info', 'comment', 'next', 'exit', 'done', 'cap']
            }

info = {'layout': "---\n"
                  "Enter the identifiers of elements you wish to group "
                  "together.\n"
                  "Separate the identifiers with a comma.\n"
                  "\n"
                  "Example of valid input: b1, a1, t1\n\n"
                  ""
                  "This command would group nodes B1, A1 and T1 under "
                  "a common node.\n"
                  "---\n"
                  "Grouping nodes may be deleted using command rm.\n\n"
                  "Example command: rm g1\n\n"
                  "This command would delete group G1.\n"
                  "---\n"
                  "Other valid commands include:\n\n"
                  "info: Print this message.\n"
                  "comment: Enter a comment about current diagram.\n"
                  "cap: Save current visualisation on disk.\n"
                  "next: Move on to the next diagram.\n"
                  "exit: Exit the annotator immediately.\n"
                  "done: Mark current diagram complete and move on.\n"
                  "---"
        }

# Define a dictionary of various prompts presented to user during annotation
prompts = {'nucleus_id': "Enter the identifier of nucleus: ",
           'satellite_id': "Enter the identifier(s) of satellite(s): ",
           'layout_default': "Please enter nodes to group or a valid command: ",
           'comment': "Enter comment: ",
           'rst_default': "Please enter a valid command: ",
           'rel_prompt': "Please enter relation name: "
           }

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
