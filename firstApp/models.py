from django.db import models

# Create your models here.

# model for to store tumour uploaded by user and also predicted result
class result(models.Model):
    image = models.FileField(upload_to = 'media')
    result = models.TextField()


class Counter(models.Model):
    count1=models.IntegerField()        