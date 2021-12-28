from django.shortcuts import render,get_object_or_404

# Create your views here.
from django.http import HttpResponse,Http404,HttpResponseRedirect
from .models import Question
from django.template import loader
from django.urls import reverse
from django.views import generic

# from .models import Choice, Question



