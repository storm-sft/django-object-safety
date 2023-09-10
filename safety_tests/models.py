from django.db import models

from service_perms.models import AbstractRemoteUser


# Create your models here.

class FakePost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()


class RemoteUser(AbstractRemoteUser):
    pass

    class Meta:
        app_label = "safety_tests"
