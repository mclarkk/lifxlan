# Lifx Tile - Web hit counter
# rename to app.py for default Flask webserver
# runs as a webserver when you run this python script with: flask run
# each of the 5 tiles count as a webhit counter with a different colour
# once a tile gets 50 hits it loops round back to 0 and illuminates 
# white pixels starting from the top left for each 50.

from flask import Flask, request
from lifxlan import *
from random import randint
from time import sleep
import json
import numpy
import sys
app = Flask(__name__)

lan = LifxLAN()
tilechain_lights = lan.get_tilechain_lights()
if len(tilechain_lights) == 0:
    print("No TileChain lights on network.")
    sys.exit()    

t = lan.get_tilechain_lights()[0]  # grab the first tilechain
print("Selected TileChain light: {}".format(t.get_label()))

web_hits=0
app_installs=0
users_registered=0
properties_added=0
properties_subscribed=0

@app.route('/reset', methods=["POST"])
def reset():
    global web_hits, app_installs, users_registered, properties_added, properties_subscribed

    web_hits=0
    app_installs=0
    users_registered=0
    properties_added=0
    properties_subscribed=0

    set_tile(4,web_hits,get_light_blue())
    set_tile(3,app_installs,get_dark_blue())
    set_tile(2,users_registered,get_purple())
    set_tile(1,properties_added,get_green())
    set_tile(0,properties_subscribed,get_gold())   
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/web', methods=["POST"])
def web_vist():
    global web_hits
    
    print(request.get_json())
    set_tile(4,web_hits,get_light_blue())
    web_hits+=1
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@app.route('/app', methods=["POST"])
def app_install():
    global app_installs
    
    print(request.get_json())
    set_tile(3, app_installs,get_purple())
    app_installs+=1
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    
@app.route('/user', methods=["POST"])
def user_registered():
    global users_registered
    
    print(request.get_json())
    set_tile(2,users_registered,get_light_green())
    users_registered+=1
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@app.route('/property', methods=["POST"])
def property_added():
    global properties_added
    
    print(request.get_json())
    set_tile(1,properties_added,get_green())
    properties_added+=1
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}     

@app.route('/sub', methods=["POST"])
def property_subscribed():
    global properties_subscribed    
    print(request.get_json())
    set_tile(0,properties_subscribed,get_gold())
    properties_subscribed+=1
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
                                      

def get_random_color():
    return randint(0, 65535), randint(0, 65535), randint(0, 65535), randint(2500, 9000)        

def set_tile(index, value, color):
    palette = {0:  get_black(),
                1: color,
                2: WHITE
                }

    matrix=generateArrayFromNumber(value)                
                
    sprite = []
    for x in range(8):
        for y in range(8):
            sprite.append(palette[matrix[x][y]])
    t.set_tile_colors(index, sprite, 2500, rapid=True)

def generateArrayFromNumber(num):

    disp_val=num%50
    num50= (num - disp_val) / 50

    array= numpy.zeros(shape=(8,8),dtype=numpy.int16)
    for x in range(8):
        for y in range(8):
            val=(x+1)+((8-(y+1))*8)
            if (val<=disp_val):
                array[y,x]=1

    for x in range(8):
        val= (x+1)
        if (val<=num50):
            array[0,x]=2

    return array

def get_dark_blue():
    return get_scaledHSV(255,100,45)

def get_light_blue():
    return get_scaledHSV(195,100,44)

def get_purple():
    return get_scaledHSV(303,75,36)      

def get_black():
    return 0,0,0,0

def get_white():
    return 0,0,65535,6500      

def get_green():
    return get_scaledHSV(132,100,39)

def get_light_green():
    return get_scaledHSV(62,100,51)    

def get_gold():
    return get_scaledHSV(24,100,56)

def get_scaledHSV(h,s,v):
    return (int)(h/360*65535),(int)(s/100*65535),(int)(v/100*65535),6500    
