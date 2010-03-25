import pygame
from const import *
from pygame.locals import *

from cellulose.extra.restrictions import StringRestriction
from cellulose import *

import label
import widget

class _button(widget.Widget):

    _label = widget.ReplaceableCellDescriptor()

    def __init__(self, **params):
        self._label = None
        super(_button,self).__init__(**params)


    def set_label(self, v):
        if hasattr(v, "value"):
            l = label.Label(v.value, parent=self)
            l._cells["value"] = ComputedCell(lambda:str(v.value))
        if type(v) == int:
            v = str(v)
        if type(v) == str or type(v) == unicode:
            l = label.Label(v, parent=self)
        self.send(CHANGE)
        self._label = l
        self._label._cells["hovering"] = self._cells["hovering"]
        self._label._cells["focused"] = self._cells["focused"]
        self._label._cells["pressing"] = self._cells["pressing"]
    label = property(lambda self: self._label, set_label)

    def width(self):
        if not self.label:
            return widget.Widget.width.function(self)
        w = self.label.width + self.style_option["padding-left"]+self.style_option["padding-right"]
        return widget.Widget.width.function(self, w)
    width = ComputedCellDescriptor(width)

    def height(self):
        if not self.label:
            return widget.Widget.height.function(self)
        h = self.label.height + self.style_option["padding-top"]+self.style_option["padding-bottom"]
        return widget.Widget.height.function(self,h)
    height = ComputedCellDescriptor(height)


    def draw_widget(self):
        self.label.dirty = True
        self.label.draw()



class Button(_button):
    """
    Button([value]) -> Button widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    A widget resembling a button.

    Arguments
    ---------
    value
        The text or widget to be displayed on the button.
    """

    _value = widget.ReplaceableCellDescriptor()

    def __init__(self, value=" ", **params):
        super(Button, self).__init__(**params)
        self._value = None
        self.value = value

    def set_value(self, v):
        self._value = v
        self.label = v

    value = property(lambda self: self._value, set_value)



class Switch(_button):
    """
    Switch([value, [labels, [options]]]) -> Switch widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    This is very similar to a button. When clicked, it will cycle through it's
    list of options. The label displayed will be the the item in the labels list
    at the same index as the current option (value) in the options list. The
    labels and options need to be exactly the same size.

    Arguments
    ---------
    value
        Must be an item in the options list.
    labels
        A list of strings that will be used as labels.
    options
        A list of items that are cycled through to determin this widgets value.
    """

    _value = widget.ReplaceableCellDescriptor()
    on_label = widget.ReplaceableCellDescriptor()
    off_label = widget.ReplaceableCellDescriptor()

    def __init__(self, value=False, labels=("Off", "On"), options=(False,True),
                **params):
        super(Switch, self).__init__(**params)
        self._value = value
        self.labels = list(labels)
        self.options = list(options)
        if len(self.labels) != len(self.options):
            raise ValueError("The number of labels has to equal the number of options!")
        self.set_value(value)


    def set_value(self, v):
        self._value = v
        if v not in self.options:
            error = """Could not find value in options.
"""
            error = error+"Value:"+str(v)+"  Options:"+str(self.options)
            raise ValueError(error)
        self.label = self.labels[self.options.index(v)]
    value = property(lambda self: self._value, set_value)

    def click(self):
        i = self.options.index(self.value)
        if i == len(self.options)-1:
            i = 0
        else:
            i += 1
        self.value = self.options[i]
