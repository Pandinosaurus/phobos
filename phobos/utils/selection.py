#!/usr/bin/python
# coding=utf-8

"""
.. module:: phobos.utils.selection
    :platform: Unix, Windows, Mac
    :synopsis: This module contains functions to find and select objects

.. moduleauthor:: Kai von Szadowski, Ole Schwiegert, Simon Reichel

Copyright 2014, University of Bremen & DFKI GmbH Robotics Innovation Center

This file is part of Phobos, a Blender Add-On to edit robot models.

Phobos is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License
as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

Phobos is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Phobos.  If not, see <http://www.gnu.org/licenses/>.
"""

import bpy
import phobos.defs as defs
from phobos.phoboslog import log


def getObjectsByPhobostypes(phobostypes):
    """Returns list of all objects in the current scene matching phobostype

    Args:
      phobostypes(list): the phobostypes to match objects with.

    Returns:
      list - Blender objects.

    """
    return [obj for obj in bpy.context.scene.objects if obj.phobostype in phobostypes]


def getChildren(root, phobostypes=(), selected_only=False, include_hidden=True):
    """Finds all (selected or unselected / hidden or unhidden) children of a
    given root object and phobostypes. If phobostypes is not provided, it is ignored.

    Args:
      root(bpy.types.Object): object to start search from.
      phobostypes(list of strings, optional): phobostypes to limit search to. (Default value = ()
      selected_only(bool.): True to find only selected children, else False.
      include_hidden(bool.): True to include hidden objects, else False.

    Returns:
      list - Blender objects which are children of root.

    """
    return [child for child in bpy.context.scene.objects if getRoot(child) == root and
            (child.phobostype in phobostypes if phobostypes else True) and
            (not child.hide or include_hidden) and
            (child.select or not selected_only)]


def getImmediateChildren(obj, phobostypes=(), selected_only=False, include_hidden=False):
    """Returns all immediate children for a given object and phobostypes (if provided).
    Search can be limited to selected objects and non-hidden objects.

    Args:
      obj(bpy.types.Object): object to start search from.
      phobostypes(list of strings, optional): phobostypes to limit search to. (Default value = ()
      selected_only(bool.): True to find only selected children, else False.
      include_hidden(bool.): True to include hidden objects, else False.

    Returns:
      list - Blender objects which are immediate children of obj.

    """
    return [child for child in obj.children if
            (child.phobostype in phobostypes if phobostypes else True) and
            (not child.hide or include_hidden) and
            (child.select or not selected_only)]


def getEffectiveParent(obj, ignore_selection=False, include_hidden=False):
    """Returns the parent of an object, i.e. the first *link* ascending the
    object tree that is selected, starting from the obj, optionally also excluding
    hidden objects.

    Args:
      obj(bpy.types.Object): object of which to find the parent.
      include_hidden(bool, optional): True to include hidden objects, else False. (Default value = False)
      ignore_selection:  (Default value = False)

    Returns:
      bpy.types.Object - the effective parent of the obj.

    """
    parent = obj.parent
    while (parent and ((parent.hide and not include_hidden) or
            (not parent.select and bpy.data.window_managers[0].phobosexportsettings.selectedOnly
             and not ignore_selection)
             or parent.phobostype != 'link')):
        parent = parent.parent
    return parent


def getRoot(obj=None):
    """Returns the root object of a model the Blender object obj or, if obj is
    not provided, the active object is part of, traversing up the tree.
    If no such object is found, returns None.

    Args:
      obj(bpy.types.Object, optional): The object to find the root for. (Default value = None)

    Returns:
      bpy.types.Object - The root object.

    """
    obj = bpy.context.active_object if obj is None else obj
    if obj is None:
        log("No root object found! Check your object selection.", "ERROR")
        return None
    else:
        child = obj
        while child.parent and not isRoot(child):
            child = child.parent
        return child


def getRoots():
    """Returns a list of all of the current scene's root links, i.e. links containing a model
    name or entity name.

    :return: list - all root links.

    Args:

    Returns:

    """
    roots = [obj for obj in bpy.context.scene.objects if isRoot(obj)]
    if roots is None:
        log("Phobos: No root objects found.", "WARNING")
    else:
        rootnames = ', '.join((root.name for root in roots))
        log("Phobos: Found {0} root object(s): {1}".format(len(roots), rootnames), "DEBUG")
    return roots  # TODO: Should we change this and all other list return values in a tuple or generator expression?


def isRoot(obj):
    """Returns whether or not the object passed to obj is a Phobos model root.

    Args:
      obj(bpy.types.Object): The object for which model root status is tested.

    Returns:
      bool - True if obj is Phobos model root, else False.

    """
    return None if obj is None else ('modelname' in obj and obj.phobostype in ['link', 'submodel']
                                     and obj.parent is None)


def isEntity(obj):
    """Returns whether or not the opject passed is an Phobos entity.

    Args:
      obj(bpy.types.Object): The object for which entity status is tested.

    Returns:
      bool - True if obj is an entity, else False.

    """
    return None if obj is None else ('entity/type' in obj and 'entity/name' in obj)


def selectObjects(objects, clear=True, active=-1):
    """Selects all objects provided in list, clears current selection if clear is True
    and sets one of the objects the active objects if a valid index is provided.

    Args:
      objects(list of bpy.types.Object): the objects to be selected.
      clear(bool, optional): clear current selection? (Default value = True)
      active(int, optional): index of the object to set active. (Default value = -1)

    Returns:
      None.

    """
    # if no object is active, object mode can't be toggled
    if bpy.context.scene.objects.active:
        bpy.ops.object.mode_set(mode='OBJECT')
    if clear:
        bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select = True
    if active >= 0:
        bpy.context.scene.objects.active = objects[active]


def getObjectByName(name):
    """Returns list of objects that either have a specific *name* or contain a custom
    name property with that name.

    As the function returns either an empty list, a unique object or a list of objects,
    it is possible to test for uniqueness of the result by calling `isinstance(result, list)`.

    Args:
      name(str): The exact object name to find.

    Returns:
      bpy.types.Object or list - one or list of objects matching name

    """
    objlist = []
    for obj in bpy.context.scene.objects:
        if name == obj.name:
            objlist.append(obj)
        else:
            for key in obj.keys():
                try:
                    if obj[key].endswith('/name') and name == obj[key]:
                        objlist.append(obj)
                except AttributeError:
                    continue
    return objlist[0] if len(objlist) == 1 else objlist


def getObjectsByPattern(pattern, match_case=False):
    """Return a list of objects in the scene that match a name pattern. The pattern
    may match either the object's actual name or the value of the 'phobostype/name'
    property.

    Args:
      pattern(str): The pattern to search for.
      match_case(bool, optional): Indicate whether to match the object names' case to the pattern. (Default value = False)

    Returns:
      list - all matching objects.

    """
    objlist = []
    for obj in bpy.data.objects:
        for key in obj.keys():
            if key.endswith('/name'):
                objname = obj[key]
                if ((match_case and pattern in objname) or
                        (not match_case and pattern.lower() in objname.lower())):
                    objlist.append(obj)
        if (match_case and pattern in obj.name) \
                or (not match_case and pattern.lower() in obj.name.lower()):
            objlist.append(obj)
    return objlist


def getObjectByNameAndType(name, phobostype):
    """Find an object with a specified phobostype and having the property
    "phobostype/'name' == name".

    Args:
      name(str): The name to search for.
      phobostype(str): The phobostype to search for.

    Returns:
      bpy.types.Object - the matching object.

    """
    # FIXME: make this API-compatible with geObjectByName
    name_tag = phobostype + "/name"
    for obj in bpy.data.objects:
        if name_tag in obj and name == obj[name_tag]:
            return obj
    log("No object of type " + phobostype + " with name " + name + " found.", "WARNING")
    return None


def selectByName(name, match_case=False, exact=False):
    """Uses getObjectsByPattern to select the found objects.

    Args:
      name(str): The name (pattern) to search for.
      match_case(bool, optional): Indicate whether to match the object names' case to the pattern. (Default value = False)
      exact(bool, optional): whether to search for exact string or not (Default value = False)

    Returns:
      None.

    """
    if exact:
        obj = getObjectByName(name)
        selectObjects(object if isinstance(obj, list) else [obj], True)
    else:
        selectObjects(getObjectsByPattern(name, match_case), True)


def getSelectedObjects():
    """Returns a generator of all selected objects independent of bpy.context.

    # DOCU fill this in
    :return:

    Args:

    Returns:

    """
    return (obj for obj in bpy.context.scene.objects if obj.select)


def getObjectsByProperty(property, value):
    # DOCU add some docstring
    candidate = None
    for obj in bpy.data.objects:
        if property in obj and obj[property] == value:
            candidate = obj
            break
    return candidate
