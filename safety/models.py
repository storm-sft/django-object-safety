from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractObjectPermission(models.Model):
    """
    Contains the fields that are common to both user and group object permissions.
    """

    permission = models.ForeignKey('auth.Permission', on_delete=models.CASCADE, verbose_name=_('Permission'))

    to = GenericForeignKey('to_ct', 'to_id')
    to_id = models.CharField(_('Target ID'), max_length=255)
    to_ct = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, verbose_name=_('Content Type'),
                              limit_choices_to={'model__in': ('user', 'group')}, related_name='entity_of')

    object_id = models.IntegerField(_('Object ID'), null=True)
    object_ct = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE,
                                  verbose_name=_('Target Content Type'), related_name='object_of', blank=True,
                                  null=True)
    object = GenericForeignKey('object_ct', 'object_id')

    class Meta:
        unique_together = (('to_ct', 'to_id', 'permission', 'object_ct', 'object_id'),)
        abstract = True

    def __str__(self):
        return f'{self.to} has {self.permission} on {self.object}'


class ObjectPermission(AbstractObjectPermission):
    class Meta(AbstractObjectPermission.Meta):
        verbose_name = _('User Object Permission')
        verbose_name_plural = _('User Object Permissions')


class AbstractObjectGroupUser(models.Model):
    """
    Intermediary model allowing storage of metadata in an object group that differs between users.
    """

    group = models.ForeignKey('safety.ObjectGroup', on_delete=models.CASCADE, verbose_name=_('Group'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))

    class Meta:
        abstract = True
        unique_together = (('group', 'user'),)

    def __str__(self):
        return f'{self.user} is in {self.group}'


class ObjectGroupUser(AbstractObjectGroupUser):
    class Meta(AbstractObjectGroupUser.Meta):
        abstract = False
        verbose_name = _('Object Group User')
        verbose_name_plural = _('Object Group Users')


class AbstractObjectGroup(models.Model):
    """
    A group of permissions for an object.
    """

    name = models.CharField(_('Name'), max_length=255)
    permissions = models.ManyToManyField('auth.Permission', verbose_name=_('Permissions'), blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through=ObjectGroupUser, verbose_name=_('Users'))

    target = GenericForeignKey('target_ct', 'target_id')
    target_id = models.IntegerField(_('Target ID'), null=True)
    target_ct = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE,
                                  verbose_name=_('Target Content Type'), related_name='obj_group_target_ct_of')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class ObjectGroup(AbstractObjectGroup):
    class Meta:
        verbose_name = _('Permission Group')
        verbose_name_plural = _('Permission Groups')
