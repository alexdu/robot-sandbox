from cellulose import *
from cellulose.extra.restrictions import *

class ReplaceableCellDescriptor(RestrictedInputCellDescriptor):
    custom_cells = set()
    def __set__(self, obj, value):
        if callable(value):
            value = ComputedCell(value)
            ReplaceableCellDescriptor.custom_cells.add(value)
        if isinstance(value, DependencyCell):
            if not hasattr(obj, '_cells'):
                obj._cells = {}
            obj._cells[self.get_name(obj.__class__)] = value
        #elif isinstance(value, Widget) and hasattr(value, "value"):
            #if not hasattr(obj, '_cells'):
                #obj._cells = {}
            #obj._cells[self.get_name(obj.__class__)] = value._cells['value']
        else:
            self.get_cell(obj).set(value)

