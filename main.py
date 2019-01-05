from horns.beast import BeastLamp
import os
import colorsys
from pprint import pprint

import atexit

import unicornhat as unicorn
unicorn.rotation(0)


### SETUP ###
CATCHEXCEPTIONS = True
DEBUG = False

beast = BeastLamp()


### CORE FUNCTIONS ###

def hex_to_rgb(value):
    h = value.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def rgb_to_hex(rgb):
    rgb=tuple(rgb)
    return '%02x%02x%02x' % rgb




##Global##

#Status
    
def global_status_clear():
    beast.stop()

#Brightness (0-100)

def global_brightness_set(val):
    if val is not None:
        val=int(val)/100.0
        beast.safesetbrightness(val)
 
 
##Static##

#Clamp

def static_clamp_set(hex, status):
    #Hex
    if hex is not None: #If a value was actually passed through HTTP
        rgb = hex_to_rgb(hex)
        if all(c<=255 for c in rgb): #If all values are within RGB range
            beast.clamp.rgb = rgb #Update colour
    #Status
    if status is not None: #If a value was actually passed through HTTP
        status = int(status)
        if status==1 and beast.clamp._running==False:
            beast.clamp.start()
        elif status==0 and beast.clamp._running==True:
            beast.clamp.stop()


##Dynamic##

#Rainbow

def dynamic_rainbow_set(speed, mode, status):
    if speed is not None:
        speed = float(speed)
        beast.rainbow.speed = speed
        
    if mode is not None:
        mode=int(mode)
        beast.rainbow.mode = mode
    
    if status is not None:
        status = int(status)
        if status==1 and beast.rainbow._running==False:
            beast.rainbow.start()
        elif status==0 and beast.rainbow._running==True:
            beast.rainbow.stop()
    
#ALSA
    
def dynamic_alsa_set(sensitivity, monitor, volume, mode, status):
    enabled = int(beast.alsa.enabled) #Check card is connected
    
    if enabled:
        if sensitivity is not None:
            sensitivity = float(sensitivity)
            beast.alsa.multiplier = sensitivity

        if monitor is not None:
            monitor = int(monitor)
            beast.alsa.micmix.setvolume(monitor)

        if volume is not None:
            volume = int(volume)
            beast.alsa.volmix.setvolume(volume)

        if mode is not None:
            mode=int(mode)
            beast.alsa.colormode = mode
        
        if status is not None:
            status = int(status)
            if status==1 and beast.alsa._running==False:
                beast.alsa.start()
            elif status==0 and beast.alsa._running==True:
                beast.alsa.stop()
 
 
##Special##

#Fade
 
def special_fade_set(minutes, target, status):
    if minutes is not None:
        minutes=int(minutes)
        beast.fade.fademins = minutes
    
    if target is not None:
        target=float(target)
        beast.fade.scalefinal = target
    
    if status is not None:
        status=int(status)
        if status==1 and beast.fade._running==False:
            beast.fade.start()
        elif status==0 and beast.fade._running==True:
            beast.fade.stop()

#Alarm
def special_alarm_set(time, lead, tail, status):
    if time is not None:
        time = time.split(":") #Split string into list
        beast.alarm.h=int(time[0])
        beast.alarm.m=int(time[1])
    
    if lead is not None:
        lead=int(lead)
        beast.alarm.leadmin=lead
    
    if tail is not None:
        tail=int(tail)
        beast.alarm.outmin=tail
    
    if status is not None:
        status=int(status)
        if status==1 and beast.alarm._running==False:
            beast.alarm.start()
        elif status==0 and beast.alarm._running==True:
            beast.alarm.stop()
    

###FLASK###
	
from flask import *

#Initial Setup
app=Flask(__name__)
app.config['DEBUG'] = DEBUG
message = ""

#Index
@app.route("/")
def index():
    return "Host exists, but please use API from now on."

#404 missing page
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    
#Catch all exceptions (eg invalid arguments raising exceptions in modules)
if CATCHEXCEPTIONS:
    @app.errorhandler(Exception)
    def all_exception_handler(e):
        print(e)
        return make_response(jsonify({'error': str(e)}), 500)


#New state system
@app.route("/api/v2/state", methods=['GET', 'POST'])
def api_state():
    if request.method == 'POST':
        payload = request.get_json()
        print("\nREQUEST:")
        pprint(payload)

        beast.set_state(payload)

    response = beast.state
    print("\nRESPONSE:")
    pprint(response)
    return jsonify(response)


#Status
@app.route("/api/v1/status/get", methods=['GET'])
def api_status_get():
    return jsonify(beast.state)

@app.route("/api/v1/status/all", methods=['GET'])
def api_status_all():
    return jsonify(beast.state)

@app.route("/api/v1/status/clear", methods=['GET'])
def api_status_clear():
    global_status_clear()
    return jsonify(beast.state)
    
    
#Brightness
@app.route("/api/v1/brightness/get", methods=['GET'])
def api_global_brightness_get():
    return jsonify(beast.state)
 
@app.route("/api/v1/brightness/set", methods=['GET', 'POST'])
def api_global_brightness_set():
    val = request.args.get('val')
    global_brightness_set(val)
    
    return jsonify(beast.state)
 
#Clamp
@app.route("/api/v1/clamp/get", methods=['GET'])
def api_static_clamp_get():
    return jsonify(beast.state)
    
@app.route("/api/v1/clamp/set", methods=['GET'])
def api_static_clamp_set():
    hex = request.args.get('hex')
    status = request.args.get('status')
    static_clamp_set(hex, status)
    
    return jsonify(beast.state)
    

#Rainbow
@app.route("/api/v1/rainbow/get", methods=['GET'])
def api_dynamic_rainbow_get():
    return jsonify(beast.state)
    
@app.route("/api/v1/rainbow/set", methods=['GET'])
def api_dynamic_rainbow_set():
    speed = request.args.get('speed')
    mode = request.args.get('mode')
    status = request.args.get('status')
    dynamic_rainbow_set(speed, mode, status)
    
    return jsonify(beast.state)
    
    
#ALSA
@app.route("/api/v1/alsa/get", methods=['GET'])
def api_dynamic_alsa_get():
    return jsonify(beast.state)
    
@app.route("/api/v1/alsa/set", methods=['GET'])
def api_dynamic_alsa_set():
    sensitivity = request.args.get('sensitivity')
    monitor = request.args.get('monitor')
    volume = request.args.get('volume')
    mode = request.args.get('mode')
    status = request.args.get('status')
    dynamic_alsa_set(sensitivity, monitor, volume, mode, status)
    
    return jsonify(beast.state)
    
    
#Fade
@app.route("/api/v1/fade/get", methods=['GET'])
def api_special_fade_get():
    return jsonify(beast.state)
    
@app.route("/api/v1/fade/set", methods=['GET'])
def api_special_fade_set():
    minutes = request.args.get('minutes')
    target = request.args.get('target')
    status = request.args.get('status')
    special_fade_set(minutes, target, status)

    return jsonify(beast.state)
    
#Alarm
@app.route("/api/v1/alarm/get", methods=['GET'])
def api_special_alarm_get():
    return jsonify(beast.state)
    
@app.route("/api/v1/alarm/set", methods=['GET'])
def api_special_alarm_set():
    time = request.args.get('time')
    lead = request.args.get('lead')
    tail = request.args.get('tail')
    status = request.args.get('status')
    special_alarm_set(time, lead, tail, status)

    return jsonify(beast.state)

    
    
### EXIT AND START ROUTINES ### 
 
def emergency_shutdown():
    #Stop all running processes
    beast.alarm.stop()
    beast.fade.stop()
    beast.stop()

atexit.register(emergency_shutdown)
    

#START SERVER

if __name__=='__main__':
    app.run(host='0.0.0.0', threaded=True)
