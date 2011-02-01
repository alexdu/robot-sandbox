import pygame
from const import *

import box
import label
import widget

try:
    set
except NameError:
    from sets import Set as set

from cellulose import *


class SelectBox(box.VBox):
    """
    SelectBox([multiple, [expand]]) -> SelectBox widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Subclasses from VBox. Like a html select box.

    You can access SelectBox.values to get a set of all selected values.

    Arguments
    ---------
    multiple
        If set to True, multiple options can be selected.

    expand
        If set to True (default) all widgets will expand to be the same width.
    """

    multiple = widget.ReplaceableCellDescriptor()

    def __init__(self, multiple=False, **params):
        box.VBox.__init__(self, **params)
        self.selected = set()#CellSet()
        self.options = CellDict()
        self.multiple = multiple

    def get_values(self):
        vs = set()
        for v in self.selected:
            vs.add(self.options[v])
        return vs
    values = property(get_values)

    def get_label(self, v):
        if hasattr(v, "value"):
            l = label.Label(v.value, parent=self, container=self)
            l._cells["value"] = ComputedCell(lambda:str(v.value))
        if type(v) == int:
            v = str(v)
        if type(v) == str or type(v) == unicode:
            l = label.Label(v, parent=self)
        return l

    def add(self, label, value):
        """
        SelectBox.add(label, value) -> Option widget
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Add an option to SelectBox.

        Arguments
        ---------
        label
            The text or widget to be displayed as the option.

        value
            The value of the option (not displayed).
        """
        label = self.get_label(label)
        label._cells["disabled"] = self._cells["disabled"]
        box.VBox.add(self, label)
        self.options[label] = value
        self.send(CHANGE)

        def click():
            if label in self.selected:
                self.selected.remove(label)
                label.selected = False
            else:
                self.selected.add(label)
                label.selected = True

            if not self.multiple:
                for l in self.options.keys():
                    if l != label:
                        l.selected = False
                self.selected = set((label,))#CellSet((label,))
        label.click = click

        return label

    def remove(self, option):
        """
        SelectBox.remove(option) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Remove option from SelectBox.

        Arguments
        ---------
        option
            Can ether be a string representing an option's value or the option
            widget.

        """
        if type(option) == str:
            for k,v in self.options.items():
                if v == option:
                    box.VBox.remove(self, self.options[k])
                    del self.options[k]
        else:
            box.VBox.remove(self, option)
            del self.options[option]
        self.send(CHANGE)

    def clear(self):
        """
        SelectBox.clear() -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        clears all options from SelectBox.
        """
        rops = set()
        for v in self.options.keys():
            rops.add(v)
        for v in rops:
            self.remove(v)
