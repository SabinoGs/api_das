# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ImageCategory import ImageClassifier
from models import Image, Classification
from NearestNeighbors import LoadData
import numpy as np
import urllib
import json
import cv2
import os


# Create your views here.

class FirstPage(View):

	http_methods_names = [u'get',u'post']

	def get(self,request):

		return render(request,'firstpage.html')


class GetCategories(View):

	http_methods_names = [u'get']

	def get(self,request):

		categories = Classification.objects.all()
		names = list()


		for obj in categories:
			names.append(obj.classification)

		# print images
		names = list(set(names))
		

		dicionario_retorno = dict()
		for i in names:
			dicionario_retorno[i] = Image.objects.filter(classification__classification__contains=i)


		return render(request,'categories.html',{'dicionario_retorno':dicionario_retorno})



class FaceDetect(View):

	http_methods_names = [u'get', u'post']

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(FaceDetect, self).dispatch(request, *args, **kwargs)

	def get(self, request):
		
		lista = Image.objects.all()
		return render(request, 'form.html',{"images":lista})

	def post(self,request):

		output = dict()

		url = request.POST["url"]
		print url

		faces = list()

		response = urllib.urlopen(url)
		data = response.read()
		
		image = np.asarray(bytearray(data),dtype="uint8")
		image = cv2.imdecode(image,cv2.IMREAD_COLOR)
		image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
		detector = cv2.CascadeClassifier(FACE_DETECTOR_PATH)


		rects = detector.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5,
			minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
		
		rects = [(int(x), int(y), int(x + w), int(y + h)) for (x, y, w, h) in rects]

		
		output['num_faces']=len(rects)
		output['faces'] = rects
		output['sucess'] = True
		 
		output['probability_response'] = ImageClassifier.image_from_url(url)
		
		
		for key,value in output['probability_response'].items():
			if(len(Classification.objects.filter(number_id=key,percentage=value[1])) == 0):
				classification = Classification()
				
				classification.number_id = key
				classification.classification = value[0]
				classification.percentage = value[1]

				classification.save()

				print key,value
			else:
				pass


		if( len(Image.objects.filter(url=url)) == 0 ):

			image = Image()
			image.url = request.POST['url']
			image.save()

			for key,value in output['probability_response'].items():
				
				classification = Classification.objects.get(number_id=key,percentage=value[1])
				image.classification.add(classification)
				image.save()
		

		
		data = LoadData.find_images(url)
		faces.append(output)
		
		images = list()

		for key,value in data.iteritems():
			i = Image.objects.get(id = key)
			images.append((i,value))
			
		print images
		return render(request,'return_similar.html',{"images":images})
