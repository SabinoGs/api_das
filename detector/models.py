from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Classification(models.Model):

	number_id = models.CharField(max_length=30) 
	classification = models.CharField(max_length=50)
	percentage = models.FloatField(null=True)

	def __str__(self):
		return self.classification, self.percentage

class Image(models.Model):

	url = models.URLField(max_length=200)
	classification = models.ManyToManyField(Classification,blank=True)

	def __str__(self):
		return self.url, self.classification.values()
