from django.db import models


# Create your models here.

class FakePost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
