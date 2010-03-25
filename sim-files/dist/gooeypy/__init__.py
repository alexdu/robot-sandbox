"""
GooeyPy - A fast, flexible, and cool looking GUI for pygame.
Copyright (C) 2007-2009  Joey Marshall
You can contact by email me at: web _at_ joey101.net

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from widget import Widget
from container import Container
from button import Button, Switch
from input import Input
from label import Label
from slider import HSlider, VSlider
from box import VBox, HBox
from selectbox import SelectBox
from const import *
from styleset import StyleSet
from textblock import TextBlock
from image import Image


__version__ = '0.2'
__url__ = "http://joey101.net/gooeypy/"
__doc__ = """
GooeyPy is the result of my need for a flexible and easy to use gui for pygame. Yes, I realize there are already guis for pygame out there. But with each one there is something I don't like. GooeyPy simply has everything the way I like it. So I'm not going to say it's the best one out there, because everyone has their own opinions. Here are some things that are different about GooeyPy:

Styling:
    I didn't like the way styling worked with other guis. Maybe I'm just spoiled by CSS in web development, but wouldn't it be nice if you could have CSS like styling for a gui? Oh woops, now you can! With GooeyPy, all widgets are stylable with CSS like attributes. Also, at any time during the application run time you can change the styling dynamically (and it will update itself)! All information related to displaying widgets are stored in the styling (that includes positioning; relative or absolute)

Integration:
    With all the guis I've tried, you have to figure out how to integrate the gui into an already made game. Sometimes that's impossible. And if it is possible, until you figure out how the gui works, it's very hard to do. GooeyPy doesn't steal your pygame events and doesn't interfear with your bliting (well, actually it can. Setting up the surfaces can be a little hairy, but there is some nice documentation to explain it all).

Dependencies:
    First of all, this isn't what you think. I'm not meaning other libs that GooeyPy depends on, but the dependencies within GooeyPy. Ok, that doesn't make a whole lot of sense... let me put it another way. You have a widget and all of the sudden you want to change the value. so you do widget.value = "hi". And it works! GooeyPy automatically knows when something changes that effects another part of itself. In this case, the value effects how the widget displays, so it will redraw itself. It works that way with everything! You never have to worry about redrawing a widget when it's dirty (and nither do I within GooeyPy, so that means a whole lot less bugs). All the dependencies are also cached.

Linking:
    Another cool thing I have is you can link values from one widget to another. So if the value of widget A changes, so does the value it's linked to in widget B.

Effects:
    I like the ability to have cool effects applied to my widgets. Now I have them.
"""


