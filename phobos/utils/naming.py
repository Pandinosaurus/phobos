#!/usr/bin/python
# coding=utf-8

"""
.. module:: phobos.utils.naming
    :platform: Unix, Windows, Mac
    :synopsis: This module contains functions to name objects

.. moduleauthor:: Kai von Szadowski, Ole Schwiegert

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


def getUniqueName(newname, names):
    i = 0
    while newname in names:
        numberstr = '.{0:03d}'.format(i)
        newname = newname[:63 - len(numberstr)] + numberstr
        i += 1
    return newname


def safelyName(obj, name, phobostype=None):
    """Assigns a name to an object in a safe way with regard to the internal
     name handling in Blender. If no phobostype is provided or the phobostype
     is the same as the object itself, the actual object is renamed, generating
     a name that no other object in Blender has, using Blender's own naming
     scheme. This prevents Blender to assign the name and change another object's
     name that previously held that name. If the *name* provided cannot be
     assigned to the object, it is stored in a custom variable '*phobostype*/name'
     Note that other '*/name' variables in the object are not updated.
     :return: str -- name of obj after function call

    Args:
      obj: 
      name: 
      phobostype:  (Default value = None)

    Returns:

    """
    objectname = name
    if not phobostype:
        phobostype = obj.phobostype
    if obj.phobostype == phobostype:
        objectname = getUniqueName(objectname, bpy.data.objects)
        obj.name = objectname
    if objectname != name:
        obj[phobostype+'/name'] = name
    return obj.name


def getObjectName(obj, phobostype=None):
    """Returns the name of an object relevant to Phobos.
    An optional *phobostype* parameter can be provided for objects with multiple
    uses, such as link objects (which also contain joint and motor information).
    If no *phobostype* is provided, the phobostype of the object is used.
    The contents of the custom property *phobostype*/name are returned, if present,
    else the object name itself is returned, stripped of namespaces.

    Args:
      obj(bpy.types.Object): object for which the name is requested
      phobostype: phobostype if relevant (e.g. 'motor') (Default value = None)

    Returns:
      str -- The object's name

    """
    if obj is None:
        return None
    nametype = phobostype if phobostype else obj.phobostype
    try:
        return obj[nametype + "/name"]
    except KeyError:
        return stripNamespaceFromName(obj.name)


def replaceNameElement(prop, old, new):
    """For all selected elements in Blender, replace an *old* part of a string *prop*erty with *new*.

    Args:
      prop: 
      old: 
      new: 

    Returns:

    """
    for obj in bpy.context.selected_objects:
        if prop in obj and obj[prop].find(old) > -1:
            obj[prop] = obj[prop].replace(old, new)


def addNamespaceToName(name, namespace):
    return namespace + "::" + name


def addNamespace(obj, namespace=None):
    """Namespaces a given blender object.

    Args:
      obj(bpy.types.Object): The object to namespace.
      namespace:  (Default value = None)

    Returns:

    """
    obj.name = safelyName(obj, addNamespaceToName(obj.name, namespace))


def stripNamespaceFromName(name):
    return name.split('::')[-1]


def removeNamespace(obj):
    """Removes the namespace from an object if present.

    Args:
      obj(bpy.types.Object): The object to remove the namespace from.

    Returns:

    """
    obj.name = safelyName(obj, stripNamespaceFromName(obj.name))


def toggleNamespace(obj, namespace=''):
    if not namespace or namespace + '::' in obj.name:
        removeNamespace(obj)
    else:
        addNamespace(obj, namespace)


def gatherNamespaces(separator='::'):
    """Gathers all existing namespaces.

    Args:
      separator:  (Default value = '::')

    Returns:

    """
    namespaces = []
    for obj in bpy.data.objects:
        if separator in obj.name:
            namespaces.append(obj.name.split(separator)[0])
    return namespaces
