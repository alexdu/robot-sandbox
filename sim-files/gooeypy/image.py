import pygame
from pygame.locals import *
from const import *

from cellulose import *

import widget

class Image(widget.Widget):
    """
    Image(value) -> Image widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Basic widget for simply displaying an image. value should be a pygame
    surface.
    """
    value = widget.ReplaceableCellDescriptor()

    def __init__(self, value, **params):
        widget.Widget.__init__(self, **params)
        self.value = value

    def draw_widget(self):
        self.blit(self.value, self.pos, clip_rect=self.value.get_rect())

    def width(self):
        return self.value.get_width()
    width = ComputedCellDescriptor(width)

    def height(self):
        return self.value.get_height()
    height = ComputedCellDescriptor(height)
