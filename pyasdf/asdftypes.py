# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

import os

from astropy.extern import six
from astropy.utils.misc import InheritDocstrings

from . import versioning


__all__ = ['format_tag', 'AsdfTypeIndex', 'AsdfType']


def format_tag(organization, standard, version, tag_name=None):
    """
    Format a YAML tag.
    """

    result = 'tag:{0}:{1}/{2}/'.format(
        organization, standard, version)
    if tag_name is not None:
        result += tag_name
    return result


class AsdfTypeIndex(object):
    """
    An index of the known `AsdfType`s.
    """

    _type_by_cls = {}
    _type_by_name = {}

    @classmethod
    def from_custom_type(cls, custom_type):
        return cls._type_by_cls.get(custom_type)

    @classmethod
    def from_yaml_tag(cls, tag):
        return cls._type_by_name.get(tag)


class AsdfTypeMeta(type):
    """
    Keeps track of `AsdfType` subclasses that are created, and stores
    them in `AsdfTypeIndex`.
    """
    def __new__(mcls, name, bases, attrs):
        cls = super(AsdfTypeMeta, mcls).__new__(mcls, name, bases, attrs)

        if hasattr(cls, 'name'):
            if 'yaml_tag' not in attrs:
                cls.yaml_tag = format_tag(
                    cls.organization,
                    cls.standard,
                    versioning.version_to_string(cls.version),
                    cls.name)

            AsdfTypeIndex._type_by_cls[cls] = cls
            AsdfTypeIndex._type_by_name[cls.yaml_tag] = cls

            for typ in cls.types:
                AsdfTypeIndex._type_by_cls[typ] = cls

        return cls


@six.add_metaclass(AsdfTypeMeta)
@six.add_metaclass(InheritDocstrings)
class AsdfType(object):
    """
    The base class of all custom types in the tree.

    Besides the attributes defined below, most subclasses will also
    override `to_tree` and `from_tree`.

    To customize how the type's schema is located, override `get_schema_path`.

    Attributes
    ----------
    name : str
        The name of the type.

    organization : str
        The organization responsible for the type.

    standard : str
        The standard the type is defined in.  For built-in ASDF types,
        this is ``"asdf"``.

    version : 3-tuple of int
        The version of the standard the type is defined in.

    types : list of Python types
        Custom Python types that, when found in the tree, will be
        converted into basic types for YAML output.
    """
    name = None
    organization = 'stsci.edu'
    standard = 'asdf'
    version = (0, 1, 0)
    types = []

    @classmethod
    def validate(cls, tree, ctx):
        """
        Validate the given tree of basic data types against the schema
        for this type.
        """
        from . import yamlutil
        yamlutil.validate_for_tag(cls.yaml_tag, tree, ctx)

    @classmethod
    def to_tree(cls, node, ctx):
        """
        Converts from a custom type to any of the basic types (dict,
        list, str, number) supported by YAML.  In most cases, must be
        overridden by subclasses.
        """
        return node.__class__.__bases__[0](node)

    @classmethod
    def from_tree(cls, tree, ctx):
        """
        Converts from basic types to a custom type.
        """
        return cls(tree)
