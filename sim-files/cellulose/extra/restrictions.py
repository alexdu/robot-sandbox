"""
cellulose.extra.restrictions
Copyright 2006 by Matthew Marshall <matthew@matthewmarshall.org>

This module contains classes for restricting Cells to certain sets of values.
(e.g., only strings, or only real numbers between 1.0 and 100.0)

Not a lot of thought went into this.  For now at least it works for abstrui.
I'm open to suggestions for this.

Right now probably the biggest thing that might need to be rethought is the way
it adjusts values to fit the restriction.  For example, if you assign a string
to a cell with a DecimalRestriction, it will automatically try to convert it to
a Decimal, only raising an exception if the string cannot be converted.  This
is the type of behavior you would want for an input field in a UI, but in
general it might not be appropriate.

"""

from cellulose import AutoCells, CellSet, ComputedCell, InputCell
from cellulose.descriptors import CellDescriptor, ComputedCellDescriptor
from decimal import Decimal

class RestrictionError(Exception):
    pass

class Restriction(object):
    def test(self, value):
        """
        Test if the value fits with the restriction.  Raise RestrictionError if
        not.
        """
        pass

    def adjust(self,value):
        """
        Return the value, adjusted to fit the restriction.  Raise
        RestrictionError if the value cannot be adjusted.
        """
        test(value)
        return value

class BooleanRestriction(Restriction):
    def test(self, value):
        if value not in (True, False):
            raise RestrictionError
    def adjust(self, value):
        return bool(value)

class DecimalRestriction(Restriction):
    def test(self, value):
        try:
            Decimal(str(value))
        except:
            raise RestrictionError

    def adjust(self, value):
        try:
            return Decimal(str(value))
        except:
            raise RestrictionError

class DecimalRangeRestriction(DecimalRestriction, AutoCells):
    def __init__(self, min=None, max=None):
        Restriction.__init__(self)
        AutoCells.__init__(self)
        self.max = max
        self.min = min

    def test(self, value):
        DecimalRestriction.test(self, value)
        if self.max is not None and value > self.max:
            raise RestrictionError
        if self.min is not None and value < self.min:
            raise RestrictionError

    def adjust(self, value):
        value = DecimalRestriction.adjust(self, value)
        return max(self.min, min(self.max, value))

class StringRestriction(Restriction):
    def test(self, value):
        if not isinstance(value, basestring): # Should I force unicode here?
            raise RestrictionError
    def adjust(self, value):
        return unicode(value)

class StringLengthRestriction(StringRestriction, AutoCells):
    def __init__(self, min=None, max=None):
        StringRestriction.__init__(self)
        AutoCells.__init__(self)
        self.max = max
        self.min = min  # I'm not sure that there is even a use for this :P

    def test(self,value):
        StringRestriction.test(self, value)
        if self.max is not None and len(value) > self.max:
            raise RestrictionError
        if self.min is not None and len(value) < self.min:
            raise RestrictionError

    def adjust(self, value):
        value = StringRestriction.adjust(self, value)
        value = value[:self.max]
        if len(value) < self.min:
            raise RestrictionError # Should this be padded with spaces instead?
        return value


class RestrictedComputedCell(ComputedCell):
    """
    RestrictedComputedCell

    A ComputedCell subclass that restricts its output.
    """
    def __init__(self, function=None, restriction=None):
        ComputedCell.__init__(self, function)

        self._restriction = restriction

    def _get_restriction(self):
        return self._restriction
    def _set_restriction(self, restriction):
        self._restriction = restriction
        self.dependency_changed()
    restriction = property(_get_restriction, _set_restriction)

    def run_function(self):
        if self.restriction:
            return self.restriction.adjust(self.function())
        else:
            return self.function()

class RestrictedInputCell(RestrictedComputedCell, InputCell):
    """
    This works like an InputCell, only when the value is read it is adjusted
    to satisfy a restriction.

    >>> r = DecimalRangeRestriction(min=0, max=10)
    >>> c = RestrictedInputCell(5, r)
    >>> print c.value
    5
    >>> c.value = 30
    >>> print c.value
    10

    Notice that the value that was explicitly set is remembered:

    >>> c.restriction.max = 20
    >>> print c.value
    20
    >>> c.restriction.max = 100
    >>> print c.value
    30
    >>> c.restriction.min = 50
    >>> print c.value
    50

    You can also choose another restriction, or disable it all together:
    >>> c.restriction = None
    >>> print c.value
    30
    >>> c.restriction = StringRestriction()
    >>> print repr(c.value)
    u'30'
    """
    def __init__(self, value=None, restriction=None):
        RestrictedComputedCell.__init__(self, lambda: self._set_value,
                restriction)
        self._set_value = value
        self._value = None

    def set(self, value):
        old = self._set_value
        self._set_value = value
        if value != old:
            self.dependency_changed()

    value = property(RestrictedComputedCell.get, set)



class RestrictedComputedCellDescriptor(ComputedCellDescriptor):
    cell_class = RestrictedComputedCell
    def __init__(self, function, restriction=None):
        ComputedCellDescriptor.__init__(self, function)
        self.restriction = restriction

    def create_new_cell(self, obj, value=None):
        bound_method = types.MethodType(self.function, obj, obj.__class__)
        return self.cell_class(bound_method, self.restriction)

    def __set__(self, obj, value):
        raise AttributeError('Cannot assign to ComputedCell')

class RestrictedInputCellDescriptor(CellDescriptor):
    cell_class = RestrictedInputCell
    def __init__(self, default=None, restriction=None):
        CellDescriptor.__init__(self)
        self.default = default
        self.restriction = restriction

    def create_new_cell(self, obj):
        return self.cell_class(value=self.default, restriction=self.restriction)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
