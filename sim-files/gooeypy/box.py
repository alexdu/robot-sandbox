import pygame
from const import *
from cellulose import *
import container
import widget


class _box(container.Container):

    expand = widget.ReplaceableCellDescriptor()

    def __init__(self, expand=True, **params):
        container.Container.__init__(self, **params)

        self.expand = expand

    def add(self, *widgets):
        super(_box, self).add(*widgets)
        self.position_widgets()

    def remove(self, widgets):
        container.Container.remove(self, widgets)
        self.position_widgets()

    def draw(self, drawbg=True):
        self.dirty = True
        container.Container.draw(self, drawbg)

class VBox(_box):
    """
    VBox([expand]) -> VBox widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    A box to automatically position widgets vertically.

    Arguments
    ---------
    expand
        If set to True (default) all widgets will expand to be the same width.
    """
    def position_widgets(self):
        y = 0
        for w in self.widgets:
            w.x = 0
            w.y = y
            y += w.height + self.style_option["spacing"]

            # I shouldn't have to do this...
            w.dirty = True

    def add(self, *widgets):
        """
        VBox.add(widgets) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        Add widgets to Container.

        Arguments
        ---------
        widgets
            can ether be a single widget or a list of widgets.
        """

        super(VBox, self).add(*widgets)
        if self.expand:
            width = self.width
            def width_func():
                w = width - (self.style_option["padding-left"] +\
                        self.style_option["padding-right"])
                if self.scrollable:
                    w -= self.vslider.width
                return w
            for w in widgets:
                w._cells['width'] = ComputedCell(width_func)



    def width(self):
        width = 0
        for w in self.widgets:
            if w.width > width:
                width = w.width

        width += self.style_option["padding-left"] + self.style_option["padding-right"]
        return widget.Widget.width.function(self, width)
    width = ComputedCellDescriptor(width)

    def height(self):
        return widget.Widget.height.function(self, self.content_height)
    height = ComputedCellDescriptor(height)

    def content_height(self):
        height = 0
        for w in self.widgets:
            height += w.height + self.style_option["spacing"]
        height -= self.style_option["spacing"]

        height += self.style_option["padding-top"] + self.style_option["padding-bottom"]
        return height
    content_height = ComputedCellDescriptor(content_height)


class HBox(_box):
    """
    HBox([expand]) -> HBox widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    A box to automatically position widgets horizontally.

    Arguments
    ---------
    expand
        If set to True (default) all widgets will expand to be the same height.
    """
    def position_widgets(self):
        x = 0
        for w in self.widgets:
            w.y = 0
            w.x = x
            x += w.width + self.style_option["spacing"]

            w.dirty = True


    def add(self, *widgets):
        """
        HBox.add(widgets) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        Add widgets to Container.

        Arguments
        ---------
        widgets
            can ether be a single widget or a list of widgets.
        """

        super(HBox, self).add(*widgets)
        if self.expand:
            height = self.height
            def height_func():
                return height - (self.style_option["padding-top"] +\
                        self.style_option["padding-bottom"])
            for w in widgets:
                w._cells['height'] = ComputedCell(height_func)



    def width(self):
        width = 0
        for w in self.widgets:
            width += w.width + self.style_option["spacing"]
        width -= self.style_option["spacing"]

        width += self.style_option["padding-left"] + self.style_option["padding-right"]
        return widget.Widget.width.function(self, width)
    width = ComputedCellDescriptor(width)


    def height(self):
        height = 0
        for w in self.widgets:
            if w.height > height:
                height = w.height

        height += self.style_option["padding-top"] + self.style_option["padding-bottom"]
        return widget.Widget.height.function(self, height)
    height = ComputedCellDescriptor(height)
