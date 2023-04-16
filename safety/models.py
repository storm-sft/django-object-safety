from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import gettext_lazy as _


class ObjectPermissionAbstract(models.Model):
    """
    Contains the fields that are common to both user and group object permissions.
    """

    permission = models.ForeignKey('auth.Permission', on_delete=models.CASCADE, verbose_name=_('Permission'))

    object_pk = models.CharField(_('object ID'), max_length=255)
    object_ct = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, verbose_name=_('Content Type'))
    object = GenericForeignKey('object_ct', 'object_pk')

    class Meta:
        abstract = True
        verbose_name = _('User object permission')
        verbose_name_plural = _('User object permissions')
        unique_together = (('user', 'permission', 'object_ct', 'object_pk'),)


class UserObjectPermission(ObjectPermissionAbstract, models.Model):
    """
    Object permissions for users.
    """

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name=_('User'))


class GroupObjectPermission(ObjectPermissionAbstract, models.Model):
    """
    Object permissions for groups.
    """

    group = models.ForeignKey('auth.Group', on_delete=models.CASCADE, verbose_name=_('Group'))
