"""
<title>Effects appliable to widgets</title>
<h1>Effects</h1>
"""


try:
    set # Only available in Python 2.4+
except NameError:
    from sets import Set as set # Python 2.3 fallback


class Pulsate:
    """
    This effect will cause the widget it is applied to to fade in and out at
    the designated speed (in the below example, 5).

    ::

        effect:pulsate 5;
    """
    def __init__(self, speed):
        self.speed = speed
        self.t = False
        self.alpha = None

        # We allow for multiple surfaces because a widget will have one for each
        # event (hover etc) that will need to be animated
        self.used_surfs = set()

        self.orig_alpha = None

    def run(self, surf):
        if not self.orig_alpha:
            self.orig_alpha = surf.get_alpha() or 255
            self.alpha = self.orig_alpha
        self.used_surfs.add(surf)
        surf.set_alpha(self.alpha)
        min_alpha = max(30, self.orig_alpha-150)
        if self.alpha <= min_alpha: self.t = True

        if not self.t:
            surf.set_alpha(self.alpha-self.speed)
            self.alpha -= self.speed
        elif self.alpha < self.orig_alpha:
            surf.set_alpha(self.alpha+self.speed)
            self.alpha += self.speed
        else:
            # All done. Clean up and set all used surfs to original opacy.
            for s  in self.used_surfs:
                s.set_alpha(self.orig_alpha)
            return False
        return True
