import pygame
from pygame.locals import *
from const import *

from cellulose import *
from cellulose.extra.restrictions import StringRestriction

import widget

class TextBlock(widget.Widget):
    """
    TextBlock(value) -> TextBlock widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Basic widget for wrapping and displaying some text. Supports line breaks
    (ether \\n or <br>)
    """
    value = widget.ReplaceableCellDescriptor(restriction=StringRestriction())

    def __init__(self, value, **params):
        widget.Widget.__init__(self, **params)

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

    def font_x(self):
        x,_ = self.pos
        return x + self.style_option["padding-left"]
    font_x = ComputedCellDescriptor(font_x)

    def font_y(self):
        _,y = self.pos
        return y + self.style_option["padding-top"]
    font_y = ComputedCellDescriptor(font_y)

    def lines(self):
        # First we need to wrap the text (split it into lines).
        char_w,line_h = self.font.size("e")
        max_chars = self.style_option["width"]/char_w
        line_w,_ = self.font.size(max_chars*"e")
        value = self.value.replace("\n", "<br>")
        value = value.replace("<br>", " <br> ")
        words = value.split(" ")
        lines = []
        line_data = ""
        for word in words:
            if word != "<br>" and self.font.size(line_data +" "+ word)[0] < line_w:
                # We can fit this word onto this line.
                line_data = line_data+" "+word
            else:
                # Flush old line and start a new one.
                lines.append(line_data.strip())
                if word != "<br>":
                    line_data = word
                else:
                    line_data = ""
        lines.append(line_data.strip())
        return lines
    lines = ComputedCellDescriptor(lines)

    def height(self):
        _,line_h = self.font.size("e")
        h = line_h*len(self.lines) + self.style_option["padding-bottom"]+\
                self.style_option["padding-top"]
        return widget.Widget.height.function(self, h)
    height = ComputedCellDescriptor(height)

    def draw_widget(self):
        linenum = 0
        _,line_h = self.font.size("e")
        for line in self.lines:
            x = self.font_x
            y = self.font_y + line_h*linenum
            self.blit(self.font.render(line, self.style_option["antialias"],
                      self.style_option["color"]), (x,y))
            linenum += 1
        #self.blit(self.font_value, (self.font_x,self.font_y))
