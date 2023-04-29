import itertools
from functools import reduce
from operator import concat

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
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


def has_perm(entities: list, perm: str, obj=None, content_type=None) -> bool:
    """
    Return True if the user has the specified permission. If obj is provided,
    the permission must be checked against obj. If the permission does not
    exist, return False.

    Args:
        entities: The users or groups to check the permission for.
        perm (string): The permission to check.
        obj: The object to check the permission.
        content_type (string): The content type of the permission.

    Returns:
        bool: True if the user has the specified permission, otherwise False.
    """

    all_have_perm = False

    for index, entity in enumerate(entities):
        if index == 0:
            all_have_perm = True
        if not all_have_perm or not entity.is_active:
            return False
        if entity.is_superuser:
            continue
        if not entity.is_authenticated:
            return False
        if obj is None:
            all_have_perm = entity.user_permissions.filter(codename=perm, content_type=content_type).exists()
            continue

        try:
            permission = Permission.objects.get(codename=perm)
        except Permission.DoesNotExist:
            return False

        if isinstance(entity, get_user_model()):
            all_have_perm = get_object_permission_model(obj).objects.filter(permission=permission, to_id=entity.id,
                                                                            to_ct=ContentType.objects.get_for_model(
                                                                                entity),
                                                                            object_id=obj.id).exists()
            # Check the PermissionGroup object
            if not all_have_perm:
                all_have_perm = get_object_group_model().objects.filter(target_id=obj.id,
                                                                        permissions__in=[permission],
                                                                        users__in=[entity]).exists()
        elif isinstance(entity, Group):
            all_have_perm = get_object_permission_model(obj).objects.filter(permission=permission, to_id=entity.id,
                                                                            to_ct=ContentType.objects.get_for_model(
                                                                                entity),
                                                                            object_id=obj.id).exists()

    return all_have_perm


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
        for group in get_object_group_model().objects.filter(users__in=[user], obj=obj):
            if has_perm(group, perm, obj):
                return True

    return False


def set_perm(entity: get_user_model() | Group, perm: str, obj: any = None, content_type: ContentType = None) -> bool:
    """
    Set a permission for a user or group.
    If the object is provided, the permission is set only on the object.
    If the object is None, the permission will be set on a model level,
    requiring the content_type argument. The content_type argument is only
    used for this purpose, it is not necessary if the object is provided
    as it will be automatically retrieved.

    Args:
        entity: The user or group to set the permission for.
        perm (string): The permission to set.
        obj: The object to set the permission on.
        content_type (ContentType): The ContentType of the object.
    """

    if obj is None:
        if content_type is None:
            raise ValueError("Content type must be provided if obj is None.")

        permission = Permission.objects.get_or_create(codename=perm, content_type=content_type)[0]

        if isinstance(entity, get_user_model()):
            entity.user_permissions.add(
                permission
            )
        elif isinstance(entity, Group):
            entity.permissions.add(
                permission
            )
        return True

    permission = Permission.objects.get_or_create(codename=perm, content_type=ContentType.objects.get_for_model(obj))[0]

    if isinstance(entity, get_user_model()):
        get_object_permission_model(obj).objects.get_or_create(permission=permission, to_id=entity.id,
                                                               to_ct=ContentType.objects.get_for_model(entity),
                                                               object_id=obj.id,
                                                               object_ct=ContentType.objects.get_for_model(obj))
        return True
    elif isinstance(entity, Group):
        get_object_permission_model(obj).objects.get_or_create(permission=permission, to_id=entity.id,
                                                               to_ct=ContentType.objects.get_for_model(entity),
                                                               object_id=obj.id,
                                                               object_ct=ContentType.objects.get_for_model(obj))
        return True

    return False


def lift_perm(entity, perm: str, obj=None, content_type: ContentType = None) -> bool:
    """
    Remove the permission for a user or group.

    Args:
        entity: The user or group to remove the permission for.
        perm (string): The permission to remove.
        obj: The object to remove the permission on.
        content_type (ContentType): The ContentType of the object.
    """

    if obj is None:
        if content_type is None:
            raise ValueError("Content type must be provided if obj is None.")
        entity.user_permissions.remove(Permission.objects.get(codename=perm, content_type=content_type))
        return True

    permission = Permission.objects.get(codename=perm, content_type=ContentType.objects.get_for_model(obj))

    if type(entity) == get_user_model():
        user_obj_perm = get_object_permission_model(obj).objects.filter(permission=permission, to_id=entity.id,
                                                                        to_ct=ContentType.objects.get_for_model(
                                                                            entity),
                                                                        object_id=obj.id,
                                                                        object_ct=ContentType.objects.get_for_model(
                                                                            obj))

        if not user_obj_perm.exists():
            return False

        user_obj_perm.delete()
        return True

    group_obj_perm = get_object_permission_model(obj).objects.filter(permission=permission, to_id=entity.id,
                                                                     to_ct=ContentType.objects.get_for_model(entity),
                                                                     object_id=obj.id,
                                                                     object_ct=ContentType.objects.get_for_model(obj)
                                                                     ).delete()
    if not group_obj_perm.exists():
        return False

    group_obj_perm.delete()
    return True


def get_perms(entity, obj=None) -> list[str]:
    """
    Get the permissions for a user or group.

    Args:
        entity: The user or group to get the permissions for.
        obj: The object to get the permissions on.
    """

    if obj is None:
        return [perm.codename for perm in
                (entity.user_permissions.all() if isinstance(entity, get_user_model()) else entity.permissions.all())]

    return [perm.permission.codename for perm in get_object_permission_model(obj).objects.filter(
        to_id=entity.id,
        to_ct=ContentType.objects.get_for_model(entity),
        object_id=obj.id,
        object_ct=ContentType.objects.get_for_model(obj)
    )]


def get_gross_perms(entity, obj=None) -> list[str]:
    """
    Get the permissions for a user or group, including permissions from groups.

    Args:
        entity: The user or group to get the permissions for.
        obj: The object to get the permissions on.
    """

    if obj is None:
        return get_perms(entity) + list(
            reduce(concat,
                   [[permission.codename for permission in group.permissions] for group in entity.groups]
                   )
        )

    return get_perms(entity, obj) + [perm.permission.codename for perm in get_object_group_model(obj).objects.filter(
        users__in=[entity],
        object=obj,
    )]


def get_users_with_perms(perms, obj=None, content_type=None, with_group_users=False) -> \
        list[get_user_model()]:
    """
    Get all users that have the specified permission(s).

    Args:
        perms: A list of permissions to check.
        obj: The object to check the permissions on.
        with_group_users: Include users in groups that have the permission in the result.
        content_type (ContentType): The ContentType of the object.

    Returns:
        list[User]: A list of users that have the permission.
    """

    if not isinstance(perms, list):
        perms = [perms]

    if obj is None:
        if content_type is None:
            raise ValueError("Content type must be provided if obj is None.")

        permissions = get_user_model().objects.filter(
            user_permissions__codename__in=perms,
            user_permissions__content_type=content_type,
        ).distinct()

        if with_group_users:
            permissions = list(permissions) + list(get_user_model().objects.filter(
                groups__permissions__codename__in=perms,
                groups__permissions__content_type=content_type,
            ).distinct())

        return permissions

    permissions = get_object_permission_model(obj).objects.filter(
        permission__codename__in=perms,
    )

    users = list(
        [permission.to for permission in permissions.filter(to_ct=ContentType.objects.get_for_model(get_user_model()))]
    )

    if with_group_users:
        if obj is None:
            groups = Group.objects.filter(groups__permissions__codename__in=perms)
        else:
            groups = get_object_group_model(obj).objects.filter(permissions__codename__in=perms, target_id=obj.id,
                                                                target_ct=ContentType.objects.get_for_model(obj))
        users += itertools.chain(*[list(group.users.all()) for group in groups])

    return users


def get_groups_with_perms(perms: list[str] | str, content_type: ContentType, obj=None) -> list[Group]:
    """
    Get all groups that have the specified permission(s).

    Args:
        perms (list[str] | str): Permission string(s) to check.
        content_type (ContentType): The content type of the model that holds the permissions.
        obj: The object, if checking for object permissions.

    Returns:
        list[Group]: A list of groups that have the permission.
    """

    if not isinstance(perms, list):
        perms = [perms]

    if obj is None and content_type is None:
        raise ValueError("Content type must be provided if obj is None.")

    if obj is None:
        return list(Group.objects.filter(permissions__codename__in=perms, permissions__content_type=content_type))

    ct = content_type if content_type else ContentType.objects.get_for_model(obj)

    permissions = get_object_permission_model(obj).objects.filter(permission__codename__in=perms,
                                                                  permission__content_type=ct,
                                                                  object_ct=ct,
                                                                  object_id=obj.id,
                                                                  to_ct=ContentType.objects.get_for_model(Group),
                                                                  ).distinct()

    return [perm.to for perm in permissions]


def get_objects_for_entity(entity: get_user_model() | Group, permissions: list[str] | str, ct: ContentType,
                           with_group_users=True) -> \
        list[any]:
    """
    Get all objects that the user has the specified permissions on.
    Args:
        entity: The user that has access to the objects.
        permissions (list[str]): The permissions required.
        ct (ContentType): The content type of the objects.
        with_group_users (bool): Include users in groups that have the permission in the result.
    """

    assert not (with_group_users is True and isinstance(entity, Group)), \
        "Entity must be a user if with_group_users is set."

    if not isinstance(permissions, list):
        permissions = [permissions]

    perms = get_object_permission_model().objects.filter(
        to_ct=ContentType.objects.get_for_model(entity),
        to_id=entity.id,
        permission__codename__in=permissions,
        permission__content_type=ct,
    )

    if with_group_users:
        obj_accesses = list(perms) + list(get_object_group_model().objects.filter(users__in=[entity]))

        objs = []

        for perm in obj_accesses:
            if isinstance(perm, get_object_permission_model(ct.model_class())):
                objs.append(perm.object)
            elif isinstance(perm, get_object_group_model(ct.model_class())):
                objs.append(perm.target)

        return objs

    return [perm.object for perm in perms]


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

    ct = ContentType.objects.get_for_model(obj)

    perm_group = get_object_group_model().objects.create(name=name, target_id=obj.id,
                                                         target_ct=ct)

    for permission in permissions:
        perm_group.permissions.add(Permission.objects.get_or_create(codename=permission, content_type=ct)[0].id)

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
