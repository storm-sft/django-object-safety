from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from safety.models import ObjectGroup
from safety.utils import get_object_group_model


def retrieve_object_group(name: str, obj) -> ObjectGroup:
    """
    Get an object group.

    Args:
        name (string): The name of the group.
        obj: The object to get the group from.

    Returns:
        Group: The group object.
    """

    return get_object_group_model().objects.get(name=name, target_id=obj.id,
                                                target_ct=ContentType.objects.get_for_model(obj))


def create_object_group(name: str, permissions: list[str], obj) -> ObjectGroup:
    """
    Create an object group.

    Args:
        name (string): The name of the group.
        permissions: The permissions to add to the group.
        obj: The object to add the group to.

    Returns:
        Group: The group object.
    """

    perm_group = get_object_group_model().objects.create(name=name, target_id=obj.id,
                                                         target_ct=ContentType.objects.get_for_model(obj))

    for permission in permissions:
        perm_group.permissions.add(Permission.objects.get_or_create(codename=permission)[0])

    return perm_group


def delete_object_group(name: str, obj) -> bool:
    """
    Remove an object group.

    Args:
        name (string): The name of the group.
        obj: The object to remove the group from.

    Returns:
        bool: True if the group was removed, otherwise False.
    """

    group = get_object_group_model().objects.filter(name=name, target_id=obj.id,
                                                    target_ct=ContentType.objects.get_for_model(obj))
    if not group.exists():
        return False

    group.delete()
    return True


def add_user_to_object_group(user: get_user_model(), name: str, obj) -> bool:
    """
    Add a user to an object group.

    Args:
        user: The user to add to the group.
        name: The name of the perm group.
        obj: The object for the perm group.

    Returns:
        bool: True if the user was added to the group, otherwise False.
    """

    get_object_group_model().objects.get(name=name, target_id=obj.id,
                                         target_ct=ContentType.objects.get_for_model(obj)).users.add(user)
    return True


def remove_user_from_object_group(user: get_user_model(), name: str, obj) -> bool:
    """
    Remove a user from an object group.

    Args:
        user: The user to remove from the group.
        name: The name of the perm group.
        obj: The object of the perm group.

    Returns:
        bool: True if the user was removed from the group, otherwise False.
    """

    user.has_perm(name, obj)

    ObjectGroup.objects.get(name=name, target_id=obj.id,
                            target_ct=ContentType.objects.get_for_model(obj)).users.remove(user)
    return True
