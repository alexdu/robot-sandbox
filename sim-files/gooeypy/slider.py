import pygame
from const import *

from cellulose import *

import widget

class _slider(widget.Widget):

    _value = widget.ReplaceableCellDescriptor()
    length = widget.ReplaceableCellDescriptor()
    min_value = widget.ReplaceableCellDescriptor()
    step = widget.ReplaceableCellDescriptor()

    def __init__(self, value=0, min_value=0, length=20, step=True, **params):
        widget.Widget.__init__(self, **params)
        self.step = step
        self.length = length
        self.min_value = min_value
        self.value = value

        # Create the marker widget and link it's values to sliders.
        self.marker = Marker()#widget.Widget()
        self.marker.parent = self
        self.marker._cells["hovering"] = self._cells["hovering"]
        self.marker._cells["focused"] = self._cells["focused"]
        self.marker._cells["pressing"] = self._cells["pressing"]
        self.marker._cells["disabled"] = self._cells["disabled"]


    def set_value(self, v):
        v = max(v, self.min_value)
        v = min(v, self.min_value+self.length)
        if self.step: v = int(v)
        self._value = v
        self.send(CHANGE)
    value = property(lambda self: self._value, set_value)


    def marker_pos(self):
        w = self.style_option["width"] - self.marker.width
        w = float(self.value-self.min_value)/(self.length) * w

        h = self.style_option["height"] - self.marker.height
        h = float(self.value-self.min_value)/(self.length) * h
        return (int(w),int(h))
    marker_pos = ComputedCellDescriptor(marker_pos)

class HSlider(_slider):
    """
    HSlider([value, [min_value, [length, [step]]]]]) -> Slider widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Arguments
    ---------
    value
        Initial value

    orient
        Can be *vertical* or *horizontail* (default)

    min_value
        This is the lowest value the slider can go to. Defaults to 0.

    length
        The largest value the slider can go to would be min_value+length.
        Defaults to min_value.

    step
        If step is True (default) the value will always be an int.
        Otherwise it won't round off the decimal.
    """

    def __init__(self, theme="default", surface=None, **params):
        _slider.__init__(self, theme=theme, surface=surface, **params)

        def width_func():
            return self.height-(self.style_option["padding-left"]+\
                    self.style_option["padding-right"])
        self.marker._cells['width'] = ComputedCell(width_func)
        def height_func():
            return self.height-(self.style_option["padding-top"]+\
                    self.style_option["padding-bottom"])
        self.marker._cells['height'] = ComputedCell(height_func)

    def draw_widget(self):
        self.marker.x = self.marker_pos[0]
        self.marker.dirty = True
        self.marker.draw()

    def event(self, e):
        widget.Widget.event(self, e)
        adj = 0
        if e.type == MOUSEBUTTONDOWN:
            if not self.marker.rect.collidepoint(e.pos):
                x,y,adj = e.pos[0]-self.pos[0],e.pos[1]-self.pos[1],1
        elif e.type == MOUSEMOTION:
            if 1 in e.buttons and self.focused:
                x = e.pos[0]-self.pos[0]
                w = self.style_option["width"] - self.marker.width
                self.value = (x - self.marker.width)*(self.length/float(w)) +\
                        self.min_value

        if adj:
            w = self.style_option["width"] - self.marker.width
            v = int((x - self.marker.width/2)*self.length/float(w)) +\
                    self.min_value
            if v > self.value:
                self.value += 1
            else:
                self.value -= 1


class VSlider(_slider):
    """
    VSlider([value, [min_value, [length, [step]]]]]) -> Slider widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Just like HSlider except displays vertically.
    """

    def __init__(self, **params):
        _slider.__init__(self, **params)

        def width_func():
            return self.width-(self.style_option["padding-left"]+\
                    self.style_option["padding-right"])
        self.marker._cells['width'] = ComputedCell(width_func)
        def height_func():
            return self.width-(self.style_option["padding-top"]+\
                    self.style_option["padding-bottom"])
        self.marker._cells['height'] = ComputedCell(height_func)

    def draw_widget(self):
        self.marker.y = self.marker_pos[1]
        self.marker.dirty = True
        self.marker.draw()

    def event(self, e):
        widget.Widget.event(self, e)
        adj = 0
        if e.type == MOUSEBUTTONDOWN:
            if not self.marker.rect.collidepoint(e.pos):
                x,y,adj = e.pos[0]-self.pos[0],e.pos[1]-self.pos[1],1
        elif e.type == MOUSEMOTION:
            if 1 in e.buttons and self.focused:
                y = e.pos[1]-self.pos[1]
                h = self.style_option["height"] - self.marker.height
                self.value = (y - self.marker.height)*(self.length/float(h)) +\
                        self.min_value

        if adj:
            h = self.style_option["height"] - self.marker.height
            v = int((y - self.marker.height/2)*self.length/float(h)) +\
                    self.min_value
            if v > self.value:
                self.value += 1
            else:
                self.value -= 1

class Marker(widget.Widget):
    def __init__(self):
        widget.Widget.__init__(self)
