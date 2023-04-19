from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import TransactionTestCase
from django_fake_model import models as f

from safety.shortcuts import set_perm, has_perm, lift_perm, create_perm_group, delete_perm_group, \
    add_user_to_perm_group, remove_user_from_perm_group


class FakePost(f.FakeModel):
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        app_label = 'safety'

    @classmethod
    def set_django_objects(cls):
        content_type = ContentType.objects.get_or_create(app_label="safety", model="fakepost")[0]
        Permission.objects.get_or_create(codename="view_fakepost", content_type=content_type, name="Can view fake post")
        Permission.objects.get_or_create(codename="change_fakepost", content_type=content_type,
                                         name="Can change fake post")
        Permission.objects.get_or_create(codename="add_fakepost", content_type=content_type, name="Can add fake post")
        Permission.objects.get_or_create(codename="delete_fakepost", content_type=content_type,
                                         name="Can delete fake post")


@FakePost.fake_me
class TestObjectPermission(TransactionTestCase):
    def setUp(self):
        self.users = []
        self.users += [get_user_model().objects.create_user(username="TestUser", password="TestPassword")]
        self.users += [get_user_model().objects.create_user(username="TestUser2", password="TestPassword")]
        self.groups = []
        self.groups += [Group.objects.create(name="TestGroup")]
        self.groups += [Group.objects.create(name="TestGroup2")]
        self.posts = []
        self.posts += [FakePost.objects.create(title="TestPost", content="TestContent")]
        self.posts += [FakePost.objects.create(title="TestPost2", content="TestContent2")]

        FakePost.set_django_objects()

        self.fake_post_ct = ContentType.objects.get_for_model(FakePost)

    def test_set_global_permission(self):
        set_perm(self.users[0], "view_fakepost", content_type=self.fake_post_ct)

        self.assertTrue(has_perm([self.users[0]], "view_fakepost", content_type=self.fake_post_ct))

    def test_set_permission(self):
        success = set_perm(self.users[0], "view_fakepost", self.posts[0])
        self.assertTrue(success)

    def test_set_group_permission(self):
        success = set_perm(self.groups[0], "view_fakepost", self.posts[0])
        self.assertTrue(success)

    def test_has_global_permission(self):
        set_perm(self.users[0], "view_fakepost",
                 content_type=self.fake_post_ct)

        self.assertTrue(has_perm([self.users[0]], "view_fakepost", content_type=self.fake_post_ct))

    def test_has_permission(self):
        set_perm(self.users[0], "view_fakepost", self.posts[0])

        self.assertTrue(has_perm([self.users[0]], "view_fakepost", self.posts[0]))

    def test_has_permission_with_multiple_users(self):
        set_perm(self.users[0], "view_fakepost", self.posts[0])
        set_perm(self.users[1], "view_fakepost", self.posts[0])

        self.assertTrue(has_perm([self.users[0], self.users[1]], "view_fakepost", self.posts[0]))

    def test_lift_global_permission(self):
        set_perm(self.users[0], "view_fakepost", content_type=self.fake_post_ct)

        lift_perm(self.users[0], "view_fakepost", content_type=self.fake_post_ct)

        self.assertFalse(has_perm([self.users[0]], "view_fakepost"))

    def test_lift_permission(self):
        set_perm(self.users[0], "view_fakepost", self.posts[0])

        lift_perm(self.users[0], "view_fakepost", self.posts[0])

        self.assertFalse(has_perm([self.users[0]], "view_fakepost", self.posts[0]))


@FakePost.fake_me
class TestPermissionGroup(TransactionTestCase):
    def setUp(self):
        self.users = []
        self.users.append(get_user_model().objects.create_user(username="TestUser", password="TestPassword"))
        self.users.append(get_user_model().objects.create_user(username="TestUser2", password="TestPassword"))

        self.posts = []
        self.posts.append(FakePost.objects.create(title="TestPost", content="TestContent"))
        self.posts.append(FakePost.objects.create(title="TestPost2", content="TestContent2"))

        FakePost.set_django_objects()

        self.fake_post_ct = ContentType.objects.get_for_model(FakePost)

    def test_create_permission_group(self):
        create_perm_group("editors",
                          ["view_fakepost", "change_fakepost", "delete_fakepost"],
                          self.posts[0])
        add_user_to_perm_group(self.users[0], "editors", self.posts[0])

        self.assertTrue(has_perm([self.users[0]], "change_fakepost", self.posts[0]))

    def test_delete_permission_group(self):
        create_perm_group("editors",
                          ["view_fakepost", "change_fakepost", "delete_fakepost"],
                          self.posts[0])

        delete_perm_group("editors", self.posts[0])

        self.assertFalse(has_perm([self.users[0]], "change_fakepost", self.posts[0]))

    def test_remove_user_from_permission_group(self):
        create_perm_group("editors",
                          ["view_fakepost", "change_fakepost", "delete_fakepost"],
                          self.posts[0])

        add_user_to_perm_group(self.users[0], "editors", self.posts[0])

        remove_user_from_perm_group(self.users[0], "editors", self.posts[0])

        self.assertFalse(has_perm([self.users[0]], "change_fakepost", self.posts[0]))

    def test_remove_permission_on_delete(self):
        create_perm_group("editors",
                          ["view_fakepost", "change_fakepost", "delete_fakepost"],
                          self.posts[0])

        add_user_to_perm_group(self.users[0], "editors", self.posts[0])

        post = self.posts[0]

        self.posts[0].delete()

        self.assertFalse(has_perm([self.users[0]], "change_fakepost", post))
