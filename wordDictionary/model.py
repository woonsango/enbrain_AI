from django.db import models
from django.conf import settings

class Post(models.Model):
    author = models.ForeignKey(settings,AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    content = models.TextField()