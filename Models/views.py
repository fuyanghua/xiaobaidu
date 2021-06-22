from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
	context = {}
	context[] = 'baidu'
	return render(request, 'search_form.html',context)