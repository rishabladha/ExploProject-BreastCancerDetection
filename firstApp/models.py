from django.db import models

# Create your models here.
class result(models.Model):
    image = models.FileField(upload_to = 'media')
    result = models.TextField()
