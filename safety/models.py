from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import gettext_lazy as _


class ObjectPermission(models.Model):
    """
    Contains the fields that are common to both user and group object permissions.
    """

    permission = models.ForeignKey('auth.Permission', on_delete=models.CASCADE, verbose_name=_('Permission'))

    to = GenericForeignKey('target_ct', 'target_id')
    to_id = models.CharField(_('Target ID'), max_length=255)
    to_ct = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, verbose_name=_('Content Type'),
                              limit_choices_to={'model__in': ('user', 'group')})

    object_id = models.CharField(_('Object ID'), max_length=255)
    object_ct = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, verbose_name=_('Content Type'))
    object = GenericForeignKey('object_ct', 'object_id')

    class Meta:
        verbose_name = _('User object permission')
        verbose_name_plural = _('User object permissions')
        unique_together = (('to_ct', 'permission', 'object_ct', 'object_pk'),)
