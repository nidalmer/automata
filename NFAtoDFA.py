#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "automata.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "automata.settings"
import django
django.setup()
import graphviz as gv
from convert.models import Automata

NULL = 'E'

automata = Automata.objects.latest('id')

alphabets = automata.alphabet_set.all()
alphabet_list = []
for alphabet in alphabets:
    alphabet_list.append(alphabet.alphabet)

states = automata.states_set.all()
states_list = []
for state in states:
    states_list.append(state.state)

initials = automata.states_set.all().filter(initial = True)
for initial_entry in initials:
    initial = initial_entry.state

finals = automata.states_set.all().filter(final = True)
final_list = []
for final_entry in finals:
    final_list.append(final_entry.state)


transitions = automata.transition_set.all()
transition_list = {}
for transition in transitions:
    if transition.current_state.state not in transition_list:
        transition_list[transition.current_state.state] = {transition.input.alphabet : [transition.next_state.state]}
    elif transition.current_state.state in transition_list and transition.input.alphabet not in transition_list[transition.current_state.state]:
        transition_list[transition.current_state.state][transition.input.alphabet] = [transition.next_state.state]
    elif transition.current_state.state in transition_list and transition.input.alphabet in transition_list[transition.current_state.state]:
        transition_list[transition.current_state.state][transition.input.alphabet].append(transition.next_state.state)


def move(states, symbol):
    """Get states reachable from input states with symbol input"""
    destinations = set()
    for state in states:
        for transition in transitions:
            if transition.current_state.state == state and transition.input.alphabet == symbol:
                destinations.update(transition.next_state.state)
    return list(destinations)


def E_closure(states):
    """Get states reachable from states along NULL transition"""
    closure_list = list(states)
    unchecked_list = list(states)
    while unchecked_list:
        state = unchecked_list.pop()
        null_transitions_list = move([state], NULL)
        for null_transition in null_transitions_list:
            if null_transition not in closure_list:
                closure_list.append(null_transition)
                unchecked_list.append(null_transition)
    return sorted(closure_list)


def add_transition(transitions, current, symbol, next):
    if current not in transitions:
        # no transitions from this state yet, add to dictionary
        transitions[current] = {symbol: [next]}
    elif symbol not in transitions:
        # no transitions from this state along this symbol yet, add
        # list with single end state along this symbol
        transitions[current][symbol] = [next]
    else:
        # There are already transitions from this state along this input,
        # Append this end state to the list
        transitions[current][symbol].append(next)

    # Make sure state is in the transitions dictionary
    if next not in transitions:
        transitions[next] = dict()

def make_dfa():
    """Return equivalent dfa object"""
    # create empty automaton to build from
    dfa_states = []
    dfa_transitions = dict()
    dfa_final = []
    dfa_alphabet = []
    for alphabet in alphabet_list:
        if alphabet != NULL:
            dfa_alphabet.append(alphabet)

    if NULL in alphabet_list:
        dfa_initial = E_closure(initial)
    else:
        dfa_initial = [initial]

    dfa_states.append(dfa_initial)

    unmarked_list = [dfa_initial]

    while(unmarked_list):
        current = unmarked_list.pop(0)

        if NULL in alphabet_list:
            for alphabet in dfa_alphabet:
                dfa_move = move(current, alphabet)
                if dfa_move:
                    dfa_state = E_closure(dfa_move)
                    if dfa_state not in dfa_states:
                        # this set of nfa states is a new dfa state
                        dfa_states.append(dfa_state)
                        unmarked_list.append(dfa_state)
                    add_transition(dfa_transitions, tuple(current), alphabet, tuple(dfa_state))
        else:
            for alphabet in dfa_alphabet:
                dfa_state = move(current, alphabet)
                if dfa_state:
                    if dfa_state not in dfa_states:
                        # this set of nfa states is a new dfa state
                        dfa_states.append(dfa_state)
                        unmarked_list.append(dfa_state)
                    add_transition(dfa_transitions, tuple(current), alphabet, tuple(dfa_state))

    for dfa_state in dfa_states:
        for i in dfa_state:
            if i in final_list:
                dfa_final.append(dfa_state)


    dot_after = gv.Digraph(format='png')
    dot_after.body.extend(['rankdir=LR', 'size="100"'])

    for state in dfa_states:
        state_name = ', '.join(state)
        if state in dfa_final:
            dot_after.attr('node', peripheries='2')
            dot_after.node(str(state), state_name)
            dot_after.attr('node', peripheries='1')
        else:
            dot_after.node(str(state), state_name)
    for transition in dfa_transitions:
        current = str(list(transition))
        if list(transition) == dfa_initial:
            dot_after.node(" ", " ", shape = 'point')
            dot_after.edge(" ", current)
        for symbol in dfa_transitions[transition]:
            for state in dfa_transitions[transition][symbol]:
                next = str(list(state))
                dot_after.edge(current, next, label=symbol)
    link = "convert/static/img/DFA" + str(automata.id)
    dot_after.render(link, view=False)
    return None

make_dfa()