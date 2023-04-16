from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from safety.models import ObjectPermission


def get_user_object_permission_model():
    """
    Retrieves the user model permission object.

    TODO: Get model from settings
    """
    return ObjectPermission


def get_group_object_permission_model():
    """
    Retrieves the group model permission object.

    TODO: Get model from settings
    """

    return ObjectPermission


def has_perm(entity, perm: str, obj=None):
    """
    Return True if the user has the specified permission. If obj is provided,
    the permission must be checked against obj. If the permission does not
    exist, automatically return false.

    Args:
        entity: The user or group to check the permission for.
        perm (string): The permission to check.
        obj: The object to check the permission.

    Returns:
        bool: True if the user has the specified permission, otherwise False.
    """

    if not entity.is_active:
        return False
    if entity.is_superuser:
        return True
    if not entity.is_authenticated:
        return False
    if obj is None:
        return entity.has_perm(perm)

    try:
        permission = Permission.objects.get(perm)
    except Permission.DoesNotExist:
        return False

    if type(entity) == get_user_model():
        return get_user_object_permission_model().objects.filter(permission=permission, to=entity,
                                                                 object_id=obj.id).exists()

    return get_group_object_permission_model().objects.filter(permission=permission, to=entity,
                                                              object_id=obj.id).exists()
