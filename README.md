# lifxlan3
> lifx lights that change when you do stuff

**lifxlan3** is my python 3.6+ take on the [lifxlan](https://github.com/mclarkk/lifxlan) library by meghan clark. it uses [lifx's LAN protocol](https://lan.developer.lifx.com/) to interact with lights on your LAN.

it allows you to control your lights in fun ways, both automatically and interactively with your keyboard, 
with many built-in routines to start. additionally, it has a cohesive API that allows for easy experimentation.

the two main ways to approach this library are a combination of the following:

1. [Group][group] 
    1. the main way of interacting with lights.
    1. `Group`s act on lights virtually simultaneously.
    1. `LifxLAN`, a special subclass of `Group`, can query for all lights
    1. even a single `Light` can be used in a `Group` unless you're trying to do something `Group` doesn't support, like set a label
    
1. [Colors][colors] and [Themes][themes] 
    1. can/will be applied to `Group`s
    1. make mixing/matching/using `Color`s much simpler
    1. `Color` and `Theme` objects can be added together
    1. they make playing around fun/easy
    1. individual `Color` objects represent, not surprisingly, a single `Color`
    1. a `Theme` allows for multiple colors to be applied simultaneously in a weighted fashion.

additionally, there's plenty of type hinting and doc stringing to help clarify the API.
one of the best ways to get around the code is just import objects and run `help` on them, or just look at the source!

## quickstart

this isn't really meant to be installed as a package, so it's probably best just to download and add to your `PYTHONPATH`.

a good place to get a feel for how this works is to check out [routines/core.py][core], but here's a quick example. (you should set `TOTAL_NUM_LIGHTS` in your `lifxlan/settings.py` ahead of time, but it's not necessary)

```python
"""set lights to a theme for 8 seconds"""
from lifxlan import LifxLAN, Themes, Colors
from time import sleep

# will query LAN for all available devices in __init__ and get all extant lights' settings in parallel
lifx = LifxLAN()  # `lifx` is a `Group` representing all lights

# can add groups and individual lights together
lifx = lifx['kitchen'] + lifx['living room 1']

# will restore group's original settings when complete
with lifx.reset_to_orig():

    # can combine themes and colors
    lifx.set_theme(Themes.snes + Themes.xmas + Colors.PYTHON_LIGHT_BLUE)  # weird theme, but ok
    lifx.turn_on()
    sleep(8)
```

## core API



## [group][group]

a `Group` acts on multiple lights virtually simultaneously, and it shares much of `Light`s API (with the exception of non-sensical things like `set_label`)

the best way to see what you can do with groups is to actually look at the [`Group`](https://github.com/sweettuse/lifxlan3/blob/master/lifxlan/group.py#L70)
class. it's pretty well documented.

`LifxLAN` is a subclass of `Group`, and will be the entry point for most functions.
it's special in that it can query all `Light` objects on your LAN.



## [colors][colors]

`Color` objects represent colors in lifx's HSBk (hue, saturation, brightness, kelvin) values, meaning that HSB are all in [0, 65536) and kelvin in [2500, 9000]

they can be:
- added together which averages the colors
- created from hex codes
- converted to/from RGBk and vice versa

the `Colors` class is just a collection of potentially commonly-used colors and other colors that i just wanted to have easy access to in the system.

## [themes][themes]

`Theme` objects represent weighted combinations of `Color`s.
they can be used by `Group`s to set lights to your favorite themes in a weighted fashion.

they can also be added together, and you can add individual `Color` objects to themes as well

## [command line](https://github.com/sweettuse/lifxlan3/blob/master/routines/cli.py)

the `cli` uses [click](https://github.com/pallets/click) to provide easy access to the various routines that exist in this library.
this will give you easy access to all the routines in [core.py][core]
as well as other, separate ones, like [morse-code][morse-code]
and [light-eq][light-eq].

to see what commands are available, simply run ```python3 cli.py```


```
python3 cli.py
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  -G, --groups TEXT           csv of group or light name[s]
  -C, --colors TEXT           csv of color[s] to apply
  -T, --themes TEXT           csv of theme[s] to apply
  -B, --brightness-pct FLOAT  how bright, from 0.0-100.0, you want the lights
                              to be
  --help                      Show this message and exit.

Commands:
  blink-color      blink lights' colors
  blink-power      blink lights' power
  breathe          make lights oscillate between darker and brighter
  cycle-themes     cycle through themes/colors passed in
  getch-test       run test on getch - press keys and see bytes
  info             display info about existing lights/groups and...
  light-eq         control lights with the computer keyboard
  morse-code       convert phrase into morse code
  point-control    move a single point around a group of lights use...
  rainbow          make lights cycle through rainbow color group
  reset            reset light colors to either DEFAULT or the first color...
  set-color-theme  set group to colors/theme
  set-whites       set lights to white in range of kelvin passed in
  turn-off         turn off lights in group
  turn-on          turn on lights in group
```

to inspect your LAN and get a feel for what colors and themes are readily available, run ```python3 cli.py info```.
this will give you a list of all your lights, all the auto groups of lights, and all colors and themes in a colorful terminal output (thank you [sty](https://github.com/feluxe/sty))



## [routines](https://github.com/sweettuse/lifxlan3/tree/master/routines)
routines are just higher level functions that let you interact with your lights in fun ways.
there are some simple routines in [core.py](https://github.com/sweettuse/lifxlan3/blob/master/routines/core.py),
but i wanted to call out some other cool ones that are in separate files:

- [morse-code][morse-code]:
translates a word or phrase into into morse code and blinks it out on your lights
- [light-eq][light-eq]:
lets you use your keyboard to control hue, saturation, brightness and kelvin in real time, like an equalizer
- [point-control](https://github.com/sweettuse/lifxlan3/blob/master/routines/point_control.py):
after setting up your lights as a grid in `init_grid` in [grid_local.py](https://github.com/sweettuse/lifxlan3/blob/master/routines/grid_local.py),
you can move a color around a selected group using the direction arrows on your keyboard

as mentioned above, these are all easily run from the `cli`

## other notes

- thank you meghan clark for the effort you put into this API. i revamped the main classes like `Device`, `Light`, `Group`, etc, but left most of the lower level API alone. it works well and i was very happy i didn't have to write it.
- this will only work in python3.6+ due to much f-string usage and reliance on dictionary ordering

---
from the original documentation:

#### LIFX LAN Protocol Implementation:

The LIFX LAN protocol specification is officially documented [here](https://lan.developer.lifx.com/). In lifxlan, you can see the underlying stream of packets being sent and received at any time by initializing the LifxLAN object with the verbose flag set: `lifx = LifxLAN(verbose = True)`. (See `examples/verbose_lan.py`.) You can also set the verbose flag if creating a Light or MultizoneLight object directly.

The files that deal with LIFX packet construction and representation are:

* **message.py** -  Defines the message fields and the basic packet structure.
* **msgtypes.py** - Provides subclasses for each LIFX message type, along with their payload constructors.
* **unpack.py** - Creates a LIFX message object from a string of binary data (crucial for receiving messages).

Happy hacking!


[core]: https://github.com/sweettuse/lifxlan3/blob/master/routines/core.py
[light-eq]: https://github.com/sweettuse/lifxlan3/blob/master/routines/light_eq.py
[morse-code]: https://github.com/sweettuse/lifxlan3/blob/master/routines/morse_code.py
[group]: https://github.com/sweettuse/lifxlan3/blob/master/lifxlan/group.py#L70
[colors]: https://github.com/sweettuse/lifxlan3/blob/master/lifxlan/colors.py
[themes]: https://github.com/sweettuse/lifxlan3/blob/master/lifxlan/themes.py
