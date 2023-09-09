from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from safety.models import ObjectPermission, ObjectGroup


def get_object_permission_model(obj=None):
    """
    Retrieves the object permission model. If obj is provided, the Meta class of
    that object will be checked for a custom object permission model.

    Args:
        obj: The model class or instance to check for a custom object permission model.
    Returns:
        An instance of an object permission model.
    """

    # pylint: disable-next=protected-access
    # noinspection PyProtectedMember
    if obj and hasattr(obj._meta, 'object_permission_model'):
        return obj.object_permission_model

    return ContentType.objects.get_model(settings.SAFETY_OBJECT_PERMISSION_MODEL) \
        if hasattr(settings, 'SAFETY_OBJECT_PERMISSION_MODEL') \
        else ObjectPermission


def get_object_group_model(obj=None):
    """
    Retrieves the object group model. If obj is provided, the Meta class of
    that object will be checked for a custom Object Group model.

    Args:
        obj: The model class or instance to check for a custom Object Group model.
    Returns:
        An instance of an Object Group model.
    """

    # pylint: disable-next=protected-access
    # noinspection PyProtectedMember
    if obj and hasattr(obj._meta, 'object_permission_model'):
        return obj.object_permission_model

    return ContentType.objects.get_model(settings.SAFETY_PERMISSION_GROUP_MODEL) \
        if hasattr(settings, 'SAFETY_OBJECT_GROUP_MODEL') \
        else ObjectGroup
