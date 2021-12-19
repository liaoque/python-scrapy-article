from django.shortcuts import render,get_object_or_404

# Create your views here.
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic

# from ..model.shares import Shares
from ..model.shares_name import SharesName

class SharesView(generic.ListView):
    template_name = 'shares/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return SharesName.objects.order_by('-id')[:5]
#
# class DetailView(generic.DetailView):
#     model = Shares
#     template_name = 'polls/detail.html'
#
#
# class ResultsView(generic.DetailView):
#     model = Shares
#     template_name = 'polls/results.html'


# def index(request):
#     latest_question_list = SharesName.objects.order_by('-id')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.html', context)

# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#
# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)
#
# def vote(request, question_id):
#     return HttpResponse("You're voting on question %s." % question_id)
