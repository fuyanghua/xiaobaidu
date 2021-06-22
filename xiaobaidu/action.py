from django.http import HttpResponse
from django.shortcuts import render,redirect
from Models import models
import json,re
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
import time
import urllib.request
from bs4 import BeautifulSoup

def analysis_input(input_text):
	result = []
	ner_driver = CkipNerChunker(level=3)
	text = [input_text[1:-1]]
	ner = ner_driver(text, use_delim=True)
	for n in ner:
		for k in n:
			if k.ner != 'PERCENT' and k.ner != 'DATE' and k.ner != 'MONEY' and k.ner != 'type':
				if k.word not in result:
					result.append(k.word)
	print(result)
	return result

def get_data(text_list):
	result_list = []
	for text in text_list:
		hp_list = models.HotPoint.objects.all()
		hpexit = False
		for hp in hp_list:
			if hp.title == text:
				result_list.append(hp.charts)
				hpexit = True
				break
		if hpexit:
			continue
		url = 'https://baike.baidu.com/item/' + urllib.parse.quote(text)
		response = urllib.request.urlopen(url)
		if not response:
			continue
		html = response.read()
		soup = BeautifulSoup(html, 'html.parser')
		title = soup.find_all('dt', class_="basicInfo-item name")
		node = soup.find_all('dd', class_="basicInfo-item value")
		if not title:
			continue
		result = {}
		titlelist = []
		infolist = []
		for i in title:
			title = i.get_text().replace('\xa0','')
			titlelist.append(title)
		for i in node:
			newnode = ''
			for n in list(i):
				newnode += str(n)
			nw = newnode.replace('\n','').replace('<br/>','、')
			res = re.sub(r'[<](.*?)[>]','',nw)
			res2 = re.sub(r'\[(.*?)\]','',res)
			info = res2.split('、')
			res3 = res2.replace('\xa0','')
			info = res3.split('、')
			infolist.append(info)
		result['00000000'] = text
		for i, j in zip(titlelist, infolist):
			result[i] = j
		result_list.append(result)
	return result_list

def search(request):
	text = request.POST.get("searchtext")
	if not text:
		rep = redirect("/welcome")
		return rep
	rep = redirect("/result")
	basetext = json.dumps(text)
	rep.set_cookie("search_text",basetext)
	return rep

def update_history(username,text):
	user = models.User.objects.get(name=username)
	oldhistory = user.history
	newhistory = ''
	if not oldhistory:
		newhistory = text
		user.history = newhistory
		user.save()
		return
	history_list = oldhistory.split(',')
	if text in history_list:
		return
	if len(history_list) >= 5:
		for h in history_list[1:]:
			newhistory += h+','
		newhistory += text
	else:
		newhistory = oldhistory + ',' + text
	user.history = newhistory
	user.save()
	return

def result(request):
	result = []
	status = request.COOKIES.get('is_login')
	username = request.COOKIES.get('username')
	if status and username:
		username = username.encode('utf-8').decode('unicode_escape')
	text = request.COOKIES.get('search_text').encode('utf-8').decode('unicode_escape')
	if not text:
		rep = redirect("/welcome")
		return rep
	if len(text) > 50:
		text = text[:50]
	pctext = '关键词:'
	hp_list = models.HotPoint.objects.all()
	for hp in hp_list:
		if text[1:-1] == hp.title:
			result.append(hp.charts)
			hp.number += 1
			hp.save()
			pctext += text
			if status and username:
				update_history(username[1:-1],text[1:-1])
			return render(request,"result.html",{'result':json.dumps(result),'pctext':pctext,'num':1})
	data = analysis_input(text)
	result = get_data(data)
	num = 1
	if len(result) > 1:
		num = 2
	if not result:
		pctext = '百度百科未收录相关信息'
	for r in result:
		if status and username:
			update_history(username[1:-1],r['00000000'])
		pctext += r['00000000']+' '
		hp_list = models.HotPoint.objects.all()
		hpexit = False
		for hp in hp_list:
			if r['00000000'] == hp.title:
				hpexit = True
				hp.number += 1
				hp.save()
				break
		if not hpexit:
			new_hp = models.HotPoint(title=r['00000000'],number=1,charts=r)
			new_hp.save()
	
	return render(request,"result.html",{'result':json.dumps(result),'pctext':pctext,'num':num})

def sign_in_submit(request):
	status = request.COOKIES.get('is_login')
	username = request.POST.get('username')
	if status and username:
		rep = redirect("/welcome")
		return rep
	if request.method == "GET":
		return render(request, "signin.html")
	password = request.POST.get("password")
	if not username or not password:
		context = {}
		context['check'] = 'empty'
		return render(request,"signin.html",context)

	userlist = models.User.objects.all()
	userexit = False
	user = models.User()
	for l in userlist:
		if l.name == username:
			userexit = True
			user = l
			break
	if not userexit:
		context = {}
		context['check'] = '用户不存在'
		return render(request,"signin.html",context)
	if password != user.password:
		context = {}
		context['check'] = '用户或密码错误'
		return render(request,"signin.html",context)
	rep = redirect("/welcome")
	rep.set_cookie("is_login", True)
	baseusername = json.dumps(username)
	rep.set_cookie("username",baseusername)
	return rep

def sign_up_submit(request):
	if request.method == "GET":
		return render(request, "signup.html")
	
	username = request.POST.get("username")
	password = request.POST.get("password")
	repassword = request.POST.get("repassword")
	
	if not username or len(username) > 10:
		context = {}
		context['check'] = '用户名错误'
		return render(request,"signup.html",context)
	if not password or len(password) > 20:
		context = {}
		context['check'] = '密码错误'
		return render(request,"signup.html",context)
	if not repassword or password != repassword:
		context = {}
		context['check'] = '两次密码不一致'
		return render(request,"signup.html",context)
	userlist = models.User.objects.all()
	userexit = False
	for l in userlist:
		if l.name == username:
			userexit = True
	if userexit:
		context = {}
		context['check'] = '用户已存在'
		return render(request,"signup.html",context)
	user_obj = models.User(name=username, password=password)
	user_obj.save()
	if not user_obj:
		return redirect("/signup")
	else:
		rep = redirect("/welcome")
		rep.set_cookie("is_login", True)
		baseusername = json.dumps(username)
		rep.set_cookie("username",baseusername)
		return rep

def logout(request):
	status = request.COOKIES.get('is_login')
	username = request.COOKIES.get('username')
	if status and username:
		rep = redirect("/welcome")
		rep.delete_cookie('username')
		rep.delete_cookie('is_login')
		return rep


def testdb(request):
	list = models.User.objects.all()
	print(list[0])
	context = {}
	context['list'] = list
	return render(request,"test.html",context)
