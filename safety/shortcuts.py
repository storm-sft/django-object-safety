from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from safety.models import ObjectPermission, PermissionGroup


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


def get_permission_group_model():
    """
    Retrieves the permission group model.

    TODO: Get model from settings
    """

    return PermissionGroup


def has_perm(entities: list, perm: str, obj=None) -> bool:
    """
    Return True if the user has the specified permission. If obj is provided,
    the permission must be checked against obj. If the permission does not
    exist, automatically return false.

    Args:
        entities: The users or groups to check the permission for.
        perm (string): The permission to check.
        obj: The object to check the permission.

    Returns:
        bool: True if the user has the specified permission, otherwise False.
    """

    for entity in entities:
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

        if type(entities) == get_user_model():
            return get_user_object_permission_model().objects.filter(permission__in=permission, to=entities,
                                                                     object_id=obj.id).exists()

        return get_group_object_permission_model().objects.filter(permission__in=permission, to=entities,
                                                                  object_id=obj.id).exists()


def has_gross_perm(users: list[get_user_model()], perm: str, obj=None) -> bool:
    """
    Same as has_perm but regards groups that a user belongs to.
    Only works with users.

    Args:
        users: The users to check the permission for.
        perm (string): The permission to check.
        obj: The object to check the permission.

    Returns:
        bool: True if the user has the specified permission directly
        or through groups, otherwise False.
    """

    has_net_perm = has_perm(users, perm, obj)

    if not has_net_perm:
        return False

    for user in users:
        for group in user.groups.all():
            if has_perm(group, perm, obj):
                return True

    return False


def set_perm(entity, perm: str, obj=None) -> bool:
    """
    Set the permission for a user or group.

    Args:
        entity: The user or group to set the permission for.
        perm (string): The permission to set.
        obj: The object to set the permission on.
    """

    if obj is None:
        entity.user_permissions.add(perm)
        return True

    permission = Permission.objects.get(perm)

    if type(entity) == get_user_model():
        get_user_object_permission_model().objects.create(permission=permission, to=entity, object_id=obj.id)
        return True

    get_group_object_permission_model().objects.create(permission=permission, to=entity, object_id=obj.id)
    return True


def lift_perm(entity, perm: str, obj=None) -> bool:
    """
    Remove the permission for a user or group.

    Args:
        entity: The user or group to remove the permission for.
        perm (string): The permission to remove.
        obj: The object to remove the permission on.
    """

    if obj is None:
        entity.user_permissions.remove(perm)
        return True

    permission = Permission.objects.get(perm)

    if type(entity) == get_user_model():
        user_obj_perm = get_user_object_permission_model().objects.filter(permission=permission, to=entity,
                                                                          object_id=obj.id)

        if not user_obj_perm.exists():
            return False

        user_obj_perm.delete()
        return True

    group_obj_perm = get_group_object_permission_model().objects.filter(permission=permission, to=entity,
                                                                        object_id=obj.id).delete()
    if not group_obj_perm.exists():
        return False

    group_obj_perm.delete()
    return True
