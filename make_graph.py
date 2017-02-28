#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "automata.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "automata.settings"
import django
django.setup()
import graphviz as gv
from convert.models import Automata


# empty image directory

folder = 'convert/static/img'
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)


automata = Automata.objects.latest('id')

states = automata.states_set.all()

transitions = automata.transition_set.all()


dot_before = gv.Digraph(format='png')
dot_before.body.extend(['rankdir=LR', 'size="100"'])

for state in states:
    if (state.final):
        dot_before.node(state.state, state.state, shape='doublecircle')
    elif (state.initial):
        dot_before.node(" ", " ", shape='point')
        dot_before.edge(" " , state.state)
        dot_before.node(state.state, state.state, shape='circle')
    else:
        dot_before.node(state.state, state.state, shape='circle')

for transition in transitions:
    dot_before.edge(transition.current_state.state, transition.next_state.state, label=transition.input.alphabet)

link = "convert/static/img/" + str(automata.id)
dot_before.render(link, view = False)
