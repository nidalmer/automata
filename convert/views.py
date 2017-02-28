from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.db import transaction
from .models import Automata, Alphabet, States
from .forms import AlphabetFormSet, StatesFormSet, TransitionFormSet
import subprocess



class IndexView(generic.ListView):
    template_name = 'convert/index.html'
    context_object_name = 'all_automatas'

    def get_queryset(self):
        return Automata.objects.all()


class DetailView(generic.DetailView):
    model = Automata
    template_name = 'convert/detail.html'
    context_object_name = 'automata'


class DFAView(generic.DetailView):
    model = Automata
    template_name = 'convert/dfa.html'
    context_object_name = 'automata'

    def get_context_data(self, **kwargs):
        data = super(DFAView, self).get_context_data(**kwargs)
        command = "python NFAtoDFA.py"
        subprocess.call(command, shell=True)
        return data



class MiniView(generic.DetailView):
    model = Automata
    template_name = 'convert/mini.html'
    context_object_name = 'automata'
    def get_context_data(self, **kwargs):
        data = super(MiniView, self).get_context_data(**kwargs)
        command = "python MiniDFA.py"
        subprocess.call(command, shell=True)
        return data

class AutomataCreate(CreateView):
    model = Automata


class AutomataAllCreate(CreateView):
    model = Automata
    fields = []

    def get_context_data(self, **kwargs):
        data = super(AutomataAllCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['alphabet'] = AlphabetFormSet(self.request.POST)
            data['states'] = StatesFormSet(self.request.POST)
        else:
            data['alphabet'] = AlphabetFormSet()
            data['states'] = StatesFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        alphabet = context['alphabet']
        states = context['states']
        with transaction.atomic():
            self.object = form.save()

            if (alphabet.is_valid() and states.is_valid()):
                alphabet.instance = self.object
                states.instance = self.object
                alphabet.save()
                states.save()
        return super(AutomataAllCreate, self).form_valid(form)


class TransitionCreate(UpdateView):
    model = Automata
    fields = []

    def get_context_data(self, **kwargs):
        data = super(TransitionCreate, self).get_context_data(**kwargs)
        states_query = States.objects.all().filter(automata = self.object)
        alphabet_query = Alphabet.objects.all().filter(automata = self.object)
        if self.request.POST:
            data['transitions'] = TransitionFormSet(self.request.POST, instance=self.object)
            for form in data['transitions']:
                form.fields['current_state'].queryset = states_query
                form.fields['next_state'].queryset = states_query
                form.fields['input'].queryset = alphabet_query
        else:
            data['transitions'] = TransitionFormSet(instance=self.object)
            for form in data['transitions']:
                form.fields['current_state'].queryset = states_query
                form.fields['next_state'].queryset = states_query
                form.fields['input'].queryset = alphabet_query
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        transitions = context['transitions']
        with transaction.atomic():
            self.object = form.save()

            if transitions.is_valid():
                transitions.instance = self.object
                transitions.save()

        command = "python make_graph.py"
        subprocess.call(command, shell=True)

        return super(TransitionCreate, self).form_valid(form)
