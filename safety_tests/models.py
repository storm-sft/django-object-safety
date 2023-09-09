from django.db import models


# Create your models here.

class FakePost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        app_label = 'safety'

    # @classmethod
    # def set_django_objects(cls):
    #     content_type = ContentType.objects.get_or_create(app_label="safety", model="fakepost")[0]
    #     Permission.objects.get_or_create(codename="view_fakepost", content_type=content_type, name="Can view fake post")
    #     Permission.objects.get_or_create(codename="change_fakepost", content_type=content_type,
    #                                      name="Can change fake post")
    #     Permission.objects.get_or_create(codename="add_fakepost", content_type=content_type, name="Can add fake post")
    #     Permission.objects.get_or_create(codename="delete_fakepost", content_type=content_type,
    #                                      name="Can delete fake post")
    #
    #     return content_type
