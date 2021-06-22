from . import views,action
from django.urls import re_path

urlpatterns = [
	re_path(r'^search$', action.search),
	re_path(r'^signup$', action.sign_up_submit),
	re_path(r'^signin$', action.sign_in_submit),
	re_path(r'^logout$', action.logout),
	re_path(r'^welcome$', views.welcome),
	re_path(r'^testdb$', action.testdb),
	re_path(r'^result$', action.result),
]