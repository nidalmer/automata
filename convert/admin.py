from django.contrib import admin
from .models import Automata, Alphabet, States, Transition


admin.site.register(Automata)
admin.site.register(Alphabet)
admin.site.register(States)
admin.site.register(Transition)
