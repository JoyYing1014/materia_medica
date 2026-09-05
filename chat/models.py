from django.db import models

# Create your models here.
class Chat(models.Model):
    question = models.TextField()