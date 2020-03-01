## First, setting up the layers 3d camera will use at game statup.


init -1 python hide:
    config.layers = ['master', 'backdrop', 'backdrop2', 'middle', 'fore', 'transient', 'screens', 'overlay']

init python:
    register_3d_layer('backdrop', 'backdrop2', 'middle', 'fore')
    camera_reset()
    layer_move("backdrop", 5000)
    layer_move("backdrop2", 3000)
    layer_move("middle", 1850)
    layer_move("fore", 1000)


image dance flipped = im.Flip("Dance!.jpg", horizontal=True)

image red = "#f00"
image cyan = "#0ff"
image yellow = "#ff0"
image blue = "#00f"
image green = "#0f0"
image purple = "#f0f"

image rap_lights:
    "red"
    pause 0.7792207792207792
    "cyan"
    pause 0.7792207792207792
    "yellow"
    pause 0.7792207792207792
    "blue"
    pause 0.7792207792207792
    "green"
    pause 0.7792207792207792
    "purple"
    pause 0.7792207792207792
    "cyan"
    pause 0.7792207792207792
    "red"
    pause 0.7792207792207792
    "blue"
    pause 0.7792207792207792
    "yellow"
    pause 0.7792207792207792
    "purple"
    pause 0.7792207792207792
    "green"
    pause 0.7792207792207792
    repeat

image rap_lights2:
    "red"
    pause 0.3896103896103896
    "cyan"
    pause 0.3896103896103896
    "yellow"
    pause 0.3896103896103896
    "blue"
    pause 0.3896103896103896
    "green"
    pause 0.3896103896103896
    "purple"
    pause 0.3896103896103896
    "cyan"
    pause 0.3896103896103896
    "red"
    pause 0.3896103896103896
    "blue"
    pause 0.3896103896103896
    "yellow"
    pause 0.3896103896103896
    "purple"
    pause 0.3896103896103896
    "green"
    pause 0.3896103896103896
    repeat

