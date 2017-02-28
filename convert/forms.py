from django.forms import ModelForm, inlineformset_factory

from .models import Automata, Alphabet, States, Transition


class AutomataForm(ModelForm):
    class Meta:
        model = Automata
        exclude = ()

class AlphabetForm(ModelForm):
    class Meta:
        model = Alphabet
        exclude = ()

class StatesForm(ModelForm):
    class Meta:
        model = States
        exclude = ()

class TransitionForm(ModelForm):
    class Meta:
        model = Transition
        exclude = ()


AlphabetFormSet = inlineformset_factory(Automata, Alphabet, form = AlphabetForm, extra=1)
StatesFormSet = inlineformset_factory(Automata, States, form = StatesForm, extra=1)
TransitionFormSet = inlineformset_factory(Automata, Transition, form = TransitionForm, extra=1)