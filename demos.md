---
layout: default
title: robot-sandbox demos
---

[robot-sandbox](index.html) demos
===================

[belt1]: screenshot-conveyor-belt-1.jpg
[belt2]: screenshot-conveyor-belt-2.jpg
[draw-rose]: screenshot-robot-drawing-rose.jpg
[hanoi]: screenshot-hanoi-towers.jpg


Towers of Hanoi
---------------

    env hanoi
    load hanoi
    exec hanoi_main

![Robot solving Towers of Hanoi][hanoi]

Conveyor belt
-------------

    env belt
    load belt
    exec belt

![Conveyor belt demo 1][belt1]

Another conveyor belt example
-----------------------------
    env ex2005
    load rez2005
    exec rez2005

![Conveyor belt demo 2][belt2]


Robot drawing
-------------
... using a ballpoint pen and paper

    env desen
    load desen
    exec rose(3,2)

![Robot drawing a rose curve][draw-rose]
