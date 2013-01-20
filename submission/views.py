# Create your views here.

from django.views import generic

from submission.models import Gym
from submission.models import State


class GymListView(generic.ListView):
    '''
    Shows a list with all konzepts
    '''

    context_object_name = "gym_list"
    model = Gym
    template_name = 'gym/list.html'


class GymCreateView(generic.CreateView):
    '''
    Shows a list with all konzepts
    '''

    model = Gym
    template_name = 'form.html'


class StateListView(generic.ListView):
    '''
    Shows a list with all states
    '''

    context_object_name = "state_list"
    model = State
    template_name = 'state/list.html'


class StateCreateView(generic.CreateView):
    '''
    Creates a new state
    '''

    model = State
    template_name = 'form.html'
