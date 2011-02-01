"""
cellulose
Copyright 2006 by Matthew Marshall <matthew@matthewmarshall.org>

A light weight library providing lazy evaluation and caching with automatic
dependency discovery and cache expiration.

Be sure to check out the docs directory of the distribution.
"""

import threading, weakref, types, warnings


# The core components of cellulose:
from cellulose.cells import DependantCell, DependencyCell, InputCell, \
        ComputedCell
from cellulose.cells import get_dependant_stack, CyclicDependencyError

# Descriptors for using cells as if they were class instance attributes:
from cellulose.descriptors import InputCellDescriptor, ComputedCellDescriptor, \
        wake_cell_descriptors

# cellulose enabled mutable data types:
from cellulose.celltypes import CellList, CellDict, CellSet, ComputedDict

# A method of watching changes inside the cellulose network from the outside:
from cellulose.observers import ObserverBank, default_observer_bank, Observer


# This needs to be placed somewhere else... (if it is even worth keeping.)
class AutoCells(object):
    """ A class for automatically cellifing attributes.

    All assigned attributes that do not start with an underscore become a cell.
    Also, all functions that start with '_get_' create computed cells.

    This class really doesn't belong in this module... if it belongs in
    cellulose at all.
    """
    def __init__(self):
        self._cells = {}
        for name in [n for n in dir(self) if n.startswith('_get_')]:
            getf = getattr(self, name)
            cell_name = name[5:]
            cell = ComputedCell(getf)
            self._cells[cell_name] = cell

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            if not name in self._cells:
                self._cells[name] = InputCell()
            self._cells[name].value = value
    def __getattr__(self, name):
        if not name in self._cells:
            return object.__getattribute__(self, name)
        else:
            return self._cells[name].value

