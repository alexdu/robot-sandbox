import pygame
from const import *

from cellulose import *

import slider
import widget

class Container(widget.Widget):
    """
    Container([scrollable]) -> Container widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    A base container widget for containing other widgets. (gosh that's
    descriptive!) scrollable is for wether or not the container is, well,
    scrollable (this feature isn't complete yet, but still usable)!
    """

    scrollable = widget.ReplaceableCellDescriptor()
    offset_x   = widget.ReplaceableCellDescriptor()
    offset_y   = widget.ReplaceableCellDescriptor()

    def __init__(self, scrollable=False, **params):
        super(Container, self).__init__(**params)
        self.widgets = CellList()
        self.scrollable = scrollable
        self.offset_x = 0
        self.offset_y = 0

        self.vslider = slider.VSlider(length=self.content_height, step=False,
                active=self.scrollable, height=self.style_option["height"]-\
                self.style_option["padding-top"]-\
                self.style_option["padding-bottom"])
        self.vslider.x = self.width - self.vslider.width-\
                self.style_option["padding-left"]-\
                self.style_option["padding-right"]
        #self.vslider.container = self
        self.vslider.parent = self
        self.offset_y=self.vslider.link("value")
        self.vslider._cells["disabled"] = self._cells["disabled"]
        self.vslider._cells["length"] = self._cells["content_height"]
        self.vslider.connect(CHANGE, self.draw_widget)


    #def width(self, width=0):
        #width = widget.Widget.width.function(self, width)
        #return width+self.vslider.width
    #width = ComputedCellDescriptor(width)

    def content_height(self):
        return 0
    content_height = ComputedCellDescriptor(content_height)


    def draw_widget(self):
        if not self.widgets: return
        for w in self.widgets:
            w.dirty = True
        self.vslider.dirty = True

    def draw(self, drawbg=True):
        if self.dirty: drawbg = False
        else: drawbg = True
        super(Container, self).draw()
        if not self.widgets: return
        for w in self.widgets:
            if w.active:
                w.draw(drawbg)
        if self.scrollable:
            self.vslider.draw(False)

    def exit(self):
        self.hovering = False
        if not self.widgets: return
        for w in self.widgets:
            w.exit()

    def event(self,e):
        widget.Widget.event(self, e)
        if not self.widgets: return
        for w in self.widgets:
            if w.active:
                w._event(e)

        if self.scrollable:
            self.vslider._event(e)

    def add(self, *widgets):
        """
        Container.add(widgets) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Add widgets to Container.

        Arguments
        ---------
        widgets
            can ether be a single widget or a list of widgets.
        """

        for w in widgets:
            if type(w) == list:
                raise ValueError("Got unexpected value. Remember that if you want to add multiple widgets to a container, do c.add(w1,w2,w3)!")
            self.widgets.append(w)
            w.container = self
            w.parent = self
            w.send(OPEN)

    def remove(self, widgets):
        """
        Container.remove(widgets) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Remove widgets from Container.

        Arguments
        ---------
        widgets
            can ether be a single widget or a list of widgets.

        """
        try: iter(widgets)
        except TypeError: widgets = [widgets]

        for w in widgets:
            self.widgets.remove(w)
            w.send(CLOSE)
        self.dirty = True

    def _next(self,orig=None):
        start = 0
        if orig and orig in self.widgets: start = self.widgets.index(orig)+1
        for w in self.widgets[start:]:
            if not w.disabled and w.focusable:
                if isinstance(w,Container):
                    if w._next():
                        return True
                else:
                    self.focus(w)
                    return True
        return False

    def next(self,w=None):
        if self._next(w): return True
        if self.container: return self.container.next(self)
