"""
cellulose.descriptors
Copyright 2006 by Matthew Marshall <matthew@matthewmarshall.org>

This module provides descriptor classes for using cells as if they were class
instance attributes.

"""

from cells import InputCell, ComputedCell
import types

class CellDescriptor(object):
    cell_class = None # Subclass should override this
    def __init__(self):
        self._name_cache = None

    def get_name(self, cls):
        """
        Finds the name that this descriptor is assigned to for the given class.
        After the first call, a cached value is returned.

        Note that the 'cls' argument is only used on the first call.  This is
        not a problem so long as all classes that this method is called with
        store the descriptor with the same attribute name (such as when
        subclassing.)
        """
        if self._name_cache:
            return self._name_cache
        for name in dir(cls):
            obj = getattr(cls, name)
            if obj is self:
                self._name_cache = name
                return name
        # This should never happen...
        raise RuntimeError('Could not find this descriptor in given class.')

    def get_cell(self, obj):
        if not hasattr(obj, '_cells'):
            obj._cells = {}
        name = self.get_name(obj.__class__)
        if not name in obj._cells:
            obj._cells[name] = self.create_new_cell(obj)
        return obj._cells[name]

    def create_new_cell(self, obj):
        return self.cell_class()

    def __get__(self, obj, type):
        if obj is None:
            return self
        return self.get_cell(obj).get()

    def __set__(self, obj, value):
        self.get_cell(obj).set(value)

class InputCellDescriptor(CellDescriptor):
    cell_class = InputCell
    def __init__(self, default=None):
        CellDescriptor.__init__(self)
        self.default = default

    def create_new_cell(self, obj):
        return self.cell_class(value=self.default)

class ComputedCellDescriptor(CellDescriptor):
    cell_class = ComputedCell
    def __init__(self, function):
        CellDescriptor.__init__(self)
        self.function = function

    def create_new_cell(self, obj, value=None):
        bound_method = types.MethodType(self.function, obj, obj.__class__)
        return self.cell_class(bound_method)

    def __set__(self, obj, value):
        raise AttributeError('Cannot assign to ComputedCell')


def wake_cell_descriptors(obj, ignore_cache=False):
    """
    Find all the cell descriptors in this object's class.

    When descriptors are used, their corrisponding cells aren't actually added
    to the instances '_cells' attribute until they are accessed.  By using this
    function you can make sure that the '_cells' attribute contains all cells
    intended for the instance.

    It takes more to document than to code :-P
    """
    cls = obj.__class__
    for name in dir(cls):    # TODO this should be cached per class.
        attr = getattr(cls, name)
        if isinstance(attr, CellDescriptor):
            attr.get_cell(obj)

