from django.db import models
from django.core.urlresolvers import reverse


class Automata(models.Model):

    def __str__(self):
        return 'A' + str(self.id)

    def get_absolute_url(self):
        return reverse('convert:detail', kwargs={'pk': self.pk})


class Alphabet(models.Model):
    alphabet = models.CharField(max_length = 10, null = True, blank = True)
    automata = models.ForeignKey(Automata, on_delete = models.CASCADE)

    def __str__(self):
        return self.alphabet


class States(models.Model):
    state = models.CharField(max_length = 10, null = True, blank = True)
    final = models.BooleanField(default = False)
    initial = models.BooleanField(default = False)
    automata = models.ForeignKey(Automata, on_delete = models.CASCADE)

    def __str__(self):
        return self.state


class Transition(models.Model):
    current_state = models.ForeignKey(States, on_delete = models.CASCADE, related_name = 'current')
    input = models.ForeignKey(Alphabet, on_delete = models.CASCADE)
    next_state = models.ForeignKey(States, on_delete = models.CASCADE, related_name = 'next')
    automata = models.ForeignKey(Automata, on_delete = models.CASCADE)

    def __str__(self):
        return "T({0}, {1}) = {2}".format(
            self.current_state,
            self.input,
            self.next_state
        )

