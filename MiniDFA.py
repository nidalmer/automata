#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "automata.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "automata.settings"
import django
django.setup()
import graphviz as gv
from convert.models import Automata
from collections import defaultdict
import itertools
from itertools import groupby


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


# move function

def move(states, symbol):
    """Get states reachable from input states with symbol input"""
    destinations = set()
    for state in states:
        for transition in transitions:
            if transition.current_state.state == state and transition.input.alphabet == symbol:
                destinations.update(transition.next_state.state)
    return list(destinations)

def reverse_move(states, symbol):
    """Get states reachable from input states with symbol input"""
    destinations = set()
    for state in states:
        for transition in transitions:
            if transition.next_state.state == state and transition.input.alphabet == symbol:
                destinations.update(transition.current_state.state)
    return list(destinations)


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

def dfs(adj_list, visited, vertex, result, key):
    visited.add(vertex)
    result[key].append(vertex)
    for neighbor in adj_list[vertex]:
        if neighbor not in visited:
            dfs(adj_list, visited, neighbor, result, key)


def merge(mergelist):
    adj_list = defaultdict(list)
    for x, y in mergelist:
        adj_list[x].append(y)
        adj_list[y].append(x)

    result = defaultdict(list)
    visited = set()
    for vertex in adj_list:
        if vertex not in visited:
            dfs(adj_list, visited, vertex, result, vertex)
    return result


def belongs_to(state, mini_states):
    for mini_state in mini_states:
        if set(mini_state).issuperset(set(state)):
            return mini_state

def refine(partition):
    active = [min(partition, key=len)]
    while (active):
        A = active.pop()
        for alphabet in alphabet_list:
            for group in partition:
                group1 = list(set(group).intersection(set(reverse_move(A, alphabet))))
                group2 = list(set(group) - set(group1))
                if group1 and group2:
                    partition = [x for x in partition if x != group]
                    if group1 not in partition and group2 not in partition:
                        partition.append(group1)
                        partition.append(group2)
                    if group in active:
                        active = [x for x in active if x != group]
                        if group1 not in active and group2 not in active:
                            active.append(group1)
                            active.append(group2)
                    elif len(group1) <= len(group2):
                        if group1 not in active:
                            active.append(group1)
                    else:
                        if group2 not in active:
                            active.append(group1)
    return partition

def minimize():
    partition = [sorted(list(set(states_list) - set(final_list))), sorted(final_list)]
    new_partition = refine(partition)
    while(new_partition is not partition):
        partition = new_partition
        new_partition = refine(partition)

    mini_states = partition
    mini_initial = belongs_to(initial, mini_states)
    mini_transitions = {}
    mini_final = []

    for state in mini_states:
        for alphabet in alphabet_list:
            next = move(state, alphabet)
            mini_next = belongs_to(next, mini_states)
            if mini_next is not None:
                add_transition(mini_transitions, tuple(state), alphabet, tuple(mini_next))
        for i in state:
            if (i in final_list) and (state not in mini_final):
                mini_final.append(sorted(state))

    dot_mini = gv.Digraph(format='png')
    dot_mini.body.extend(['rankdir=LR', 'size="100"'])

    for state in mini_states:
        state_name = ', '.join(state)
        if state in mini_final:
            dot_mini.attr('node', peripheries='2')
            dot_mini.node(str(state), state_name)
            dot_mini.attr('node', peripheries='1')
        else:
            dot_mini.node(str(state), state_name)
    for transition in mini_transitions:
        current = str(list(transition))
        if list(transition) == mini_initial:
            dot_mini.node(" ", " ", shape='point')
            dot_mini.edge(" ", current)
        for symbol in mini_transitions[transition]:
            for state in mini_transitions[transition][symbol]:
                next = str(list(state))
                dot_mini.edge(current, next, label=symbol)
    link = "convert/static/img/Mini" + str(automata.id)
    dot_mini.render(link, view=False)

    return None

minimize()