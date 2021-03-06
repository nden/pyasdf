# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

import os

import numpy as np

from astropy.tests.helper import pytest

from ... import AsdfFile
from .. import main


def get_file_sizes(dirname):
    files = {}
    for filename in os.listdir(dirname):
        path = os.path.join(dirname, filename)
        if os.path.isfile(path):
            files[filename] = os.stat(path).st_size
    return files


def test_explode_then_implode(tmpdir):
    x = np.arange(0, 10, dtype=np.float)

    tree = {
        'science_data': x,
        'subset': x[3:-3],
        'skipping': x[::2],
        'not_shared': np.arange(10, 0, -1, dtype=np.uint8)
        }

    path = os.path.join(str(tmpdir), 'original.asdf')
    with AsdfFile(tree) as ff:
        ff.write_to(path)
        assert len(ff.blocks) == 2

    result = main.main_from_args(['explode', path])

    assert result == 0

    files = get_file_sizes(str(tmpdir))

    assert 'original.asdf' in files
    assert 'original_exploded.asdf' in files
    assert 'original_exploded0000.asdf' in files
    assert 'original_exploded0001.asdf' in files
    assert 'original_exploded0002.asdf' not in files

    assert files['original.asdf'] > files['original_exploded.asdf']

    path = os.path.join(str(tmpdir), 'original_exploded.asdf')
    result = main.main_from_args(['implode', path])

    files = get_file_sizes(str(tmpdir))

    assert 'original_exploded_all.asdf' in files
    assert files['original_exploded_all.asdf'] == files['original.asdf']


def test_file_not_found(tmpdir):
    path = os.path.join(str(tmpdir), 'original.asdf')
    assert main.main_from_args(['explode', path]) == 2
