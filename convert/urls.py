from django.conf.urls import url
from . import views


app_name = 'convert'

urlpatterns = [
    # /
    url(r'^$', views.AutomataAllCreate.as_view(), name = 'Index'),

    # /id
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name = 'detail'),
    url(r'automata/(?P<pk>[0-9]+)/$', views.TransitionCreate.as_view(), name='transition-add'),
    url(r'automata/dfa/(?P<pk>[0-9]+)/$', views.DFAView.as_view(), name='dfa'),
    url(r'automata/mini/(?P<pk>[0-9]+)/$', views.MiniView.as_view(), name='mini'),

]