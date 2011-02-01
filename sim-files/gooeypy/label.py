import pygame
from pygame.locals import *
from const import *

from cellulose import *
from cellulose.extra.restrictions import StringRestriction

import widget

class Label(widget.Widget):
    """
    Label(value) -> Label widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Basic widget for simply displaying some text. Not really much to
    it, you can pass it a value which it will display.
    """
    value = widget.ReplaceableCellDescriptor(restriction=StringRestriction())

    def __init__(self, value, **params):
        super(Label,self).__init__(self, **params)

        self.value = value

    def font(self):
        """
        Label.font -> pygame.Font
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        The font that this label is using.
        """
        f = self.get_font(self.style_option["font-family"], self.style_option["font-size"])
        if self.style_option["font-weight"] == "bold":
            f.set_bold(True)
        return f
    font = ComputedCellDescriptor(font)

    def width(self):
        w = self.font.size(self.value)[0]
        return widget.Widget.width.function(self,w)
    width = ComputedCellDescriptor(width)

    def height(self):
        h = self.font.size(self.value)[1]
        return widget.Widget.height.function(self,h)
    height = ComputedCellDescriptor(height)

    def font_x(self):
        x,_ = self.pos
        return x + self.style_option["padding-left"]
    font_x = ComputedCellDescriptor(font_x)

    def font_y(self):
        _,y = self.pos
        return y + self.style_option["padding-top"]
    font_y = ComputedCellDescriptor(font_y)

    #def clip_rect(self):
        #return pygame.Rect(0,0,
                #self.width-(self.style_option["padding-left"]+\
                #self.style_option["padding-right"]),
                #self.height-(self.style_option["padding-top"]+\
                #self.style_option["padding-bottom"]))
    #clip_rect = ComputedCellDescriptor(clip_rect)


    def font_value(self):
        return self.font.render(self.value,
                                self.style_option["antialias"],
                                self.style_option["color"])
    font_value = ComputedCellDescriptor(font_value)

    def draw_widget(self):
        # We do this incase we are trying to blit the text into a space smaller
        # than it can fit into.

        self.blit(self.font_value, (self.font_x,self.font_y), clip_rect=self.clip_rect)
