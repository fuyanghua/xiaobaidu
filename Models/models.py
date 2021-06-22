from django.db import models

# Create your models here

class HotPoint(models.Model):
	title = models.CharField(max_length=50)
	number = models.IntegerField()
	charts = models.JSONField(null = True)

class User(models.Model):
	name = models.CharField(max_length=10)
	password = models.CharField(max_length=20)
	history = models.CharField(max_length=50,null = True)