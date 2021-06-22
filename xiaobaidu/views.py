from django.shortcuts import render
from django.http import HttpResponse
from Models import models

def sign_in(request):
	context = {}
	context['name'] = 'sign in'
	return render(request, 'signin.html',context)

def welcome(request):
	context = {}
	hot_list = []
	hp_list = models.HotPoint.objects.all().order_by("-number")
	if len(hp_list) <= 5:
		for hp in hp_list:
			hot_list.append(hp.title)
	else:
		for hp in hp_list[0:5]:
			hot_list.append(hp.title)
	context['hotlist'] = hot_list
	status = request.COOKIES.get('is_login')
	if not status:
		return render(request,'index.html',context)
	username = request.COOKIES.get('username')
	if not username:
		return render(request,'index.html',context)
	context['username'] = username
	name = username.encode('utf-8').decode('unicode_escape')[1:-1]
	user = models.User.objects.get(name=name)
	if user.history:
		history_list = user.history.split(',')
		context['historylist'] = history_list
	return render(request, 'welcome.html',context)

