""" <title>Styling options</title> """
import os
import pygame

from cellulose import *

from descriptor import ReplaceableCellDescriptor

class Style:
    def __init__(self, styleset, values):
        self.styleset = styleset
        self.widget = styleset.widget
        self.path = self.widget.path
        self.values = values
        self.setup(values)

    def setup(self):
        pass

    def render(self):
        pass

    def draw_rect(self, surf, color, rect, width=0):
        pygame.draw.rect(surf, color, rect, width)

    def get_image_path(self, path):
        if os.path.isfile(os.path.join(self.path, path)):
            path = os.path.join(self.path, path)
        return path

    def get_image(self, path):
        if type(path) != str:
            image = pygame.image.load(path)
            if image.get_colorkey():
                return image.convert()
            else:
                return image.convert_alpha()
        path = self.get_image_path(path)
        return self.really_get_image(path)

    imagestore = {}
    def really_get_image(self, path, nocache=False):
        """ really_get_image(path, [colorkey, [nocache]]) -> pygame.Surface

        path should be a sting. Example: really_get_image("data/image/my_image.png")
        Use forward slashed as demonstrated even if you are developing under
        windows, it will open the files os independent. """

        #print path

        if Style.imagestore.has_key(path):
            return Style.imagestore[path]
        else:
            key = path.split("/")
            if len(key) == 1:
                key = key[0]
            else:
                p = ""
                for k in key:
                    p = os.path.join(p, k)
                key = p
            if path[0] == "/":
                # HACK: shouldn't have to do this... (and won't work on windows)
                key = "/"+key
            if not os.path.isfile(key):
                key = os.path.join(os.path.dirname(__file__), key)
                if not os.path.isfile(key):
                    print key
                    print "could not find image"
                    sys.exit()
            image = pygame.image.load(key)
            if image.get_colorkey():
                image = image.convert()
            else:
                image = image.convert_alpha()

            # Add it so it doesn't have to create surf again for this image.
            if not nocache:
                Style.imagestore.update({path: image})

        return image



class Opacity(Style):
    def setup(self, values):
        if len(values) == 1:
            values = values[0]
        self.values = int(values)
        # TODO: actually set alpha (or maybe do in draw func?).
        self.styleset.applied_styles["opacity"] = self

    def render(self):
        self.styleset.surface.set_alpha(None)
        self.styleset.surface.set_alpha(self.values)



class BgColor(Style):
    def setup(self, values):
        self.color = None
        if values[0] != "none":
            if type(values[0]) == str:
                color = values[0][1:-1].split(",")
                self.color = [int(c) for c in color]
            else:
                self.color = values[0]

        self.styleset.applied_styles["bgcolor"] = self


    def render(self):
        if not self.color: return
        self.rect = self.styleset.surface.get_rect()
        # If there is a border, need to scale down so it doesn't
        # overlap it.
        if self.styleset.applied_styles.has_key("border"):
            w = int(self.styleset.applied_styles["border"].values[0])
            self.rect.x += w
            self.rect.y += w
            self.rect.width -= w*2
            self.rect.height -= w*2

        self.draw_rect(self.styleset.surface, self.color, self.rect)


class Border(Style):
    def setup(self, values):
        color = values[1][1:-1].split(",")
        self.color = [int(c) for c in color]
        self.width = int(values[0])
        self.styleset.applied_styles["border"] = self

    def render(self):
        self.draw_rect(self.styleset.surface, self.color, self.styleset.surface.get_rect(), self.width)


class BgImage(Style):
    def setup(self, values):
        if values[0] != "none":
            self.im = self.get_image(values[0])
            self.colorkey = self.im.get_colorkey()
            self.style = None
            if len(values) > 1:
                self.style = values[1]
        else:
            self.style = "none"
        self.styleset.applied_styles["bgimage"] = self


    def render(self):
        if self.style == "none": return
        if not self.style or self.style == "no-repeat":
            self.styleset.surface.blit(self.im, (0,0))

        if self.style == "repeat" or self.style == "repeat-x"\
        or self.style == "repeat-y":
            num_x = self.styleset.surface.get_width() / self.im.get_width() +\
                    self.im.get_width()
            num_y = self.styleset.surface.get_height() / self.im.get_height() +\
                    self.im.get_height()

            if self.style == "repeat-y":
                for n in xrange(num_y):
                    x = 0
                    y = n*self.im.get_height()
                    self.styleset.surface.blit(self.im, (x,y))
            elif self.style == "repeat-x":
                for n in xrange(num_x):
                    x = n*self.im.get_width()
                    y = 0
                    self.styleset.surface.blit(self.im, (x,y))
            elif self.style == "repeat":
                for x in xrange(num_x):
                    for y in xrange(num_y):
                        xx = x*self.im.get_width()
                        yy = y*self.im.get_height()
                        self.styleset.surface.blit(self.im, (xx,yy))

        elif self.style == "slice":
            w = self.im.get_width()/2 - 1
            h = self.im.get_height()/2 - 1
            tl = self.im.subsurface((0, 0, w, h))
            bl = self.im.subsurface((0, self.im.get_height()-h, w, h))
            tr = self.im.subsurface((self.im.get_width()-w, 0, w, h))
            br = self.im.subsurface((self.im.get_width()-w, self.im.get_height()-h, w, h))
            l = self.im.subsurface((0, h, w, 2))
            r = self.im.subsurface((self.im.get_width()-w, h, w, 2))
            t = self.im.subsurface((w, 0, 2, h))
            b = self.im.subsurface((w, self.im.get_height()-h, 2, h))
            c = self.im.get_at((w+1, h+1))

            num_x = self.styleset.surface.get_width()  / t.get_width() + 1
            num_y = self.styleset.surface.get_height() / l.get_height() + 1

            center_rect = pygame.Rect(w, h, self.styleset.surface.get_rect().w - 2 * w, self.styleset.surface.get_rect().h - 2 * h)
            pygame.draw.rect(self.styleset.surface, c, center_rect)
            for x in xrange(w, self.styleset.surface.get_width() - w, t.get_width()):
                self.styleset.surface.blit(t, (x, 0))
                self.styleset.surface.blit(b, (x, self.styleset.surface.get_height()-t.get_height()))
            for y in xrange(h, self.styleset.surface.get_height() - h, l.get_height()):
                self.styleset.surface.blit(l, (0, y))
                self.styleset.surface.blit(r, (self.styleset.surface.get_width()-r.get_width(), y))
            self.styleset.surface.blit(tl, (0,0))
            self.styleset.surface.blit(bl, (0,self.styleset.surface.get_height()-h))
            self.styleset.surface.blit(tr, (self.styleset.surface.get_width()-w,0))
            self.styleset.surface.blit(br, (self.styleset.surface.get_width()-w,self.styleset.surface.get_height()-h))


class Color(Style):
    def setup(self, values):
        if len(values) != 3:
            color = values[0][1:-1].split(",")
            self.values = [int(c) for c in color]
        else: self.values = values
        self.styleset.applied_styles["color"] = self


class Padding(Style):
    def setup(self, values):
        padding = {}
        if len(values) == 1:
            top = right = bottom = left = values[0]
        elif len(values) == 2:
            top = bottom = values[0]
            left = right = values[1]
        elif len(values) == 4:
            top, right, bottom, left = values

        padding["top"] = int(top)
        padding["right"] = int(right)
        padding["bottom"] = int(bottom)
        padding["left"] = int(left)

        for k in ("top", "left", "right", "bottom"):
            key = "padding-"+k
            if not self.styleset.applied_styles[key]:
                self.styleset.applied_styles[key] = padding[k]



class Effect(Style):
    def setup(self, values):
        if len(values) == 1 and values[0] != "none":
            values.append("10")
        self.styleset.applied_styles["effect"] = values








class StyleSet(object):
    """
    StyleSet(widget, [parent]) -> StyleSet object
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    A styleset is a collection of style options grouped together for a
    specific event for a widget. Each widget has an dictionary named
    "stylesets" which contains several stylesets. For example::

        {"disabled":styleset, "hover":styleset, "default":styleset,
                "focused":styleset, "down":styleset}

    When the widget is hovered for example it will use stylesets["hover"]
    At any time you can change a styling option for a widget by doing
    something like this::

        mywidget.stylesets["hover"]["color"] = (255,10,10)

    Style options
    -------------

    ===============  =======================================================
    option           value
    ===============  =======================================================
    padding          8 4 4 5 | 4 5 | 10
    padding-top      3
    padding-right    3
    padding-bottom   3
    padding-left     3
    color            (255,255,255)
    font-weight      normal | bold
    font-family      Verra.ttf
    font-size        12
    effect           pulsate 5
    width            300
    height           200
    x                57
    y                102
    position         relative | absolute
    bgcolor          (200,0,0)
    bgimage          image.png repeat|repeat-x|repeat-y|no-repeat|slice
    border           3 (0,250,20)
    spacing          12 # For certain container widgets.
    opacity          25 # Alpha value. Valid otpions between 0 and 255.
    antialias        1 | 0
    align            left | right | center
    valign           top | bottom | center
    ===============  =======================================================

    Something to note about align and valign. When they are changed from their
    default values (top and left), the x and y values act as an offset. So if
    you are aligning a widget center and have an x value of 100, the widget will
    display 100 pixels to the right of the center of it's parent (or container)
    widget.

    Also, aligning only takes effect when positioning is relative (which is
    default).


    Arguments
    ---------
    widget
        The widget this styleset is for.

    parent
        Another styleset that this styleset should inherit from.
    """

    parent = ReplaceableCellDescriptor()
    widget = ReplaceableCellDescriptor()
    has_opacity = ReplaceableCellDescriptor()
    colorkey = ReplaceableCellDescriptor()

    # Setting a default style option here will make it use it at all times
    # unless explicitly set. In other words, inheriting doesn't work for these
    # options.
    default_styles = {
        "padding-top":0,
        "padding-right":0,
        "padding-bottom":0,
        "padding-left":0,
        "spacing":0,
        "font-weight":"normal",
        "effect":"none",
        "width":0,
        "height":0,
        "x":0,
        "y":0,
        "position":"relative",
        }

    styles = {
        "opacity":Opacity,
        "bgcolor":BgColor,
        "border":Border,
        "bgimage":BgImage,
        "color":Color,
        "padding":Padding,
        "effect":Effect,
    }

    def __init__(self, widget, parent=None):
        self.widget = widget
        self.parent = parent
        self._applied_styles = CellDict(self.default_styles)

        self.has_opacity = False
        self.colorkey = None

        def __getitem__(v):
            return self.__getitem__(v)
        self._applied_styles.__getitem__ = __getitem__

    # We make this read only so people can only modify the applied_styles and
    # not reassign it.
    applied_styles = property(lambda self: self._applied_styles)


    def surf(self):
        """
        StyleSet.surf -> pygame.Surface
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        The surface generated from the styling.
        """
        if self.parent:
            self.surface = self.parent.surf.copy()
        else:
            size = (int(self.widget.width), int(self.widget.height))
            if self.colorkey:
                self.surface = pygame.Surface(size)
                self.surface.fill(self.colorkey)
            else:
                self.surface = pygame.Surface(size, pygame.SRCALPHA)

        # Surfaces that use opacity have to turn off the per-pixel alphas
        if self.has_opacity:
            self.surface = self.surface.convert()
        if self.colorkey:
            self.surface = self.surface.convert()
            self.surface.set_colorkey(self.colorkey)

        for s in self.applied_styles.values():
            if hasattr(s, "render"):
                s.render()
        return self.surface
    surf = ComputedCellDescriptor(surf)


    def __getitem__(self, v):
        r = None
        if self.applied_styles.has_key(v):
            r = self.applied_styles[v]
        if not r and self.parent:
            r = self.parent[v]
        if hasattr(r, "value"): r = r.value
        return r

    def __setitem__(self, k, v):
        self.apply(k, v)


    def apply(self, option, values):
        """
        StyleSet.apply(surf, option, values) -> pygame.Surface
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Applies styling to surf. If you are just wanting to change a style
        option, use::

            StyleSet["option"] = values

        This function is mainly for internal use.
        """
        option = option.replace("_", "-")
        o = option.replace("-", "_")
        if type(values) == str or type(values) == int:
            if type(values) == str:
                values = values.split(" ")
            else: values = [values]
        if o in self.styles:
            self.styles[o](self, values)
        else:
            self.generic(option, values)
        if o == 'opacity':
            self.has_opacity = True


    def generic(self, n, v):
        if type(v) == list:
            if len(v) == 1:
                v = v[0]
                v = str(v)
                try:
                    v = int(v)
                except ValueError:
                    pass
        self.applied_styles[n] = v
