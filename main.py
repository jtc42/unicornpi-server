from horns import beast
import os
import colorsys

import atexit

import unicornhat as unicorn
unicorn.rotation(0)


### SETUP ###
CATCHEXCEPTIONS = True
DEBUG = False

### CORE FUNCTIONS ###

def hex_to_rgb(value):
    h = value.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def rgb_to_hex(rgb):
    rgb=tuple(rgb)
    return '%02x%02x%02x' % rgb

def any_running():
    return not(all(not(mod._running) for mod in beast.modlist))


##Global##

#Status
def global_status_get():
    return {'global_status': int(any_running())}
    
def global_status_all():
    out={}
    out.update(global_status_get())
    out.update(global_brightness_get())
    out.update(static_clamp_get())
    out.update(dynamic_rainbow_get())
    out.update(dynamic_alsa_get())
    out.update(special_fade_get())
    out.update(special_alarm_get())
    return out
    
def global_status_clear():
    beast.stopall()
    beast.core.clear()

#Brightness (0-100)
def global_brightness_get():
    return {'global_brightness_val': int(beast.core.getbrightness()*100)}

def global_brightness_set(val):
    if val is not None:
        val=int(val)/100.0
        beast.safesetbrightness(val)
 
 
##Static##

#Clamp
def static_clamp_get():
    hex = str(rgb_to_hex(beast.clamp.rgb))
    status = int(beast.clamp._running)
    return {'static_clamp_hex': hex, 'static_clamp_status': status}

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
def dynamic_rainbow_get():
    speed = beast.rainbow.speed
    mode = beast.rainbow.mode
    status = int(beast.rainbow._running)
    return {'dynamic_rainbow_speed': speed, 'dynamic_rainbow_mode': mode, 'dynamic_rainbow_status': status}

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
def dynamic_alsa_get():
    enabled = int(beast.alsa.enabled)
    
    if enabled:
        sensitivity = beast.alsa.multiplier
        monitor = beast.alsa.micmix.getvolume()[0]
        volume = beast.alsa.volmix.getvolume()[0]
        mode = beast.alsa.colormode
        status = int(beast.alsa._running)
        return {'dynamic_alsa_enabled': enabled, 'dynamic_alsa_sensitivity': sensitivity, 'dynamic_alsa_monitor': monitor, 'dynamic_alsa_volume': volume, 'dynamic_alsa_mode': mode, 'dynamic_alsa_status': status}
    else:
        return {'dynamic_alsa_enabled': enabled}
    
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
def special_fade_get():
    minutes = beast.special.fade.fademins
    target = beast.special.fade.scalefinal
    status = int(beast.special.fade._running)
    return {'special_fade_minutes': minutes, 'special_fade_target': target, 'special_fade_status': status}
 
def special_fade_set(minutes, target, status):
    if minutes is not None:
        minutes=int(minutes)
        beast.special.fade.fademins = minutes
    
    if target is not None:
        target=float(target)
        beast.special.fade.scalefinal = target
    
    if status is not None:
        status=int(status)
        if status==1 and beast.special.fade._running==False:
            beast.special.fade.start()
        elif status==0 and beast.special.fade._running==True:
            beast.special.fade.stop()

#Alarm
def special_alarm_get():
    time=str(beast.special.alarm.h)+':'+str(beast.special.alarm.m)+':'+str(beast.special.alarm.s)
    lead = beast.special.alarm.leadmin
    tail = beast.special.alarm.outmin
    status = int(beast.special.alarm._running)
    active = int(beast.special.alarm.SequenceStarted)
    return {'special_alarm_time': time, 'special_alarm_lead': lead, 'special_alarm_tail': tail, 'special_alarm_status': status, 'special_alarm_active': active}
    
def special_alarm_set(time, lead, tail, status):
    if time is not None:
        time = time.split(":") #Split string into list
        beast.special.alarm.h=int(time[0])
        beast.special.alarm.m=int(time[1])
    
    if lead is not None:
        lead=int(lead)
        beast.special.alarm.leadmin=lead
    
    if tail is not None:
        tail=int(tail)
        beast.special.alarm.outmin=tail
    
    if status is not None:
        status=int(status)
        if status==1 and beast.special.alarm._running==False:
            beast.special.alarm.start()
        elif status==0 and beast.special.alarm._running==True:
            beast.special.alarm.stop()
    

    

###FLASK###
	
from flask import *

#Initial Setup
app=Flask(__name__)
app.config['DEBUG'] = DEBUG
message = ""

#Server shutdown procedure
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

	
###WEB FRONT END###

#INDEX
@app.route("/")
#@requires_auth
def index():
    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)


#BRIGHTNESS
@app.route("/brightness", methods=['GET'])
def brightness():
    # Get the value from the submitted form
    global_brightness_set(float(request.args.get('brightness')))
    message="Brightness set"

    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)


#FADE
@app.route("/fade", methods=['GET'])
def fade():
    # Get the value from the submitted form

    beast.special.fade.fademins=int(request.args.get('fademin'))
    beast.special.fade.scalefinal=float(request.args.get('scalefinal'))
	
    if beast.special.fade._running==False:
        beast.special.fade.start()
    message="Fade started"

    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)

@app.route("/fade/stop")
def stopfade():
    if beast.special.fade._running==True:
        beast.special.fade.stop()
		
        message="Fade stopped"
		
    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)

    
#HLS CLAMP
@app.route("/hls", methods=['GET'])
def hls():
    # Get the value from the submitted form
    hueval = float(request.args.get('hueslider'))
    lightval = float(request.args.get('lightslider'))

    rgb = colorsys.hls_to_rgb(hueval/360, lightval/100, 1)

    beast.clamp.rgb=[int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255)]

    if beast.clamp._running==False:
        beast.clamp.start()

    message="Colours set"

    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)
    

#THERMAL CLAMP
@app.route("/thermal", methods=['GET'])
def thermal():
    # Get the value from the submitted form
    beast.clamp.temp = int(request.args.get('lamptemp')) #Update clamps stored temperature (used for web frontend, not necesarry for basic operation)
    beast.clamp.rgb = beast.core.temptorgb(beast.clamp.temp)

    if beast.clamp._running==False: #Start clamp if not already running
        beast.clamp.start()
    
    message="Lamp on"

    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)


#RAINBOW (rainbow)
@app.route("/rainbow", methods=['GET'])
def rainbow():
    # Get the value from the submitted form
    beast.rainbow.speed = float(request.args.get('speed'))/2
    
    if request.args.get('rainmode') != "nochange":
        beast.rainbow.mode = int(request.args.get('rainmode'))

    if beast.rainbow._running==False:
        beast.rainbow.start()
    
    message="Pooping rainbows"

    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)
 
    
#ALSA (alsa)
@app.route("/alsa", methods=['GET'])
def alsa():
    # Get the value from the submitted form
    beast.alsa.multiplier = float(request.args.get('sensitivity'))
    print("Set multiplier")

    if request.args.get('alsamode') != "nochange":
        beast.alsa.colormode = int(request.args.get('alsamode'))
    print("Set mode")

    beast.alsa.volmix.setvolume(int(request.args.get('volume')))
    print("Set Volume")
    beast.alsa.micmix.setvolume(int(request.args.get('gain')))
    print("Set Gain")

    if beast.alsa._running==False:
        beast.alsa.start()

    message="ALSA Started"

    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)
    
    
#ALARM (alarm)
@app.route("/alarm", methods=['GET'])
def alarm():
    # Get the value from the submitted form
    time = str(request.args.get('time')).split(":")
    
    lead=int(request.args.get('lead'))
    out=int(request.args.get('out'))
    
    beast.special.alarm.leadmin=lead
    beast.special.alarm.outmin=out
    
    beast.special.alarm.h=int(time[0])
    beast.special.alarm.m=int(time[1])

    if beast.special.alarm._running == False:
        beast.special.alarm.start()
    
    message = None

    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)

@app.route("/alarm/stop")
def stopalarm():
    if beast.special.alarm._running==True:
        beast.special.alarm.stop()
		
        message="Alarm unset"
		
    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)


#CLEAR
@app.route('/clear')
def url_clear():
	beast.stopall()
	beast.core.clear()
	return render_template('index.html', message=message, beast=beast, colorsys=colorsys)
    
	
#EXIT
@app.route('/shutdown')
#@requires_auth
def url_shutdown():
	#Stop all running processes
    beast.stopall()
    beast.special.alarm.stop()
    beast.special.fade.stop()
    beast.core.clear()
    print("Server shutting down...")
    shutdown_server()
    message="Server now offline"
    return render_template('index.html', message=message, beast=beast, colorsys=colorsys)
 

 
###API###

#Errors

#404 missing page
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    
#Catch all exceptions (eg invalid arguments raising exceptions in modules)
if CATCHEXCEPTIONS:
    @app.errorhandler(Exception)
    def all_exception_handler(e):
        app.logger.error('Unhandled Exception: %s', (e))
        return make_response(jsonify({'error': str(e)}), 500)
    
#Status
@app.route("/api/1.0/status/get", methods=['GET'])
def api_status_get():
    return jsonify(global_status_get())

@app.route("/api/1.0/status/all", methods=['GET'])
def api_status_all():
    return jsonify(global_status_all())

@app.route("/api/1.0/status/clear", methods=['GET'])
def api_status_clear():
    global_status_clear()
    return jsonify(global_status_get())
    
    
#Brightness
@app.route("/api/1.0/brightness/get", methods=['GET'])
def api_global_brightness_get():
    return jsonify(global_brightness_get())
 
@app.route("/api/1.0/brightness/set", methods=['GET'])
def api_global_brightness_set():
    val = request.args.get('val')
    global_brightness_set(val)
    
    return jsonify(global_brightness_get())
 
 
#Clamp
@app.route("/api/1.0/clamp/get", methods=['GET'])
def api_static_clamp_get():
    return jsonify(static_clamp_get())
    
@app.route("/api/1.0/clamp/set", methods=['GET'])
def api_static_clamp_set():
    hex = request.args.get('hex')
    status = request.args.get('status')
    static_clamp_set(hex, status)
    
    return jsonify(static_clamp_get())
    

#Rainbow
@app.route("/api/1.0/rainbow/get", methods=['GET'])
def api_dynamic_rainbow_get():
    return jsonify(dynamic_rainbow_get())
    
@app.route("/api/1.0/rainbow/set", methods=['GET'])
def api_dynamic_rainbow_set():
    speed = request.args.get('speed')
    mode = request.args.get('mode')
    status = request.args.get('status')
    dynamic_rainbow_set(speed, mode, status)
    
    return jsonify(dynamic_rainbow_get())
    
    
#ALSA
@app.route("/api/1.0/alsa/get", methods=['GET'])
def api_dynamic_alsa_get():
    return jsonify(dynamic_alsa_get())
    
@app.route("/api/1.0/alsa/set", methods=['GET'])
def api_dynamic_alsa_set():
    sensitivity = request.args.get('sensitivity')
    monitor = request.args.get('monitor')
    volume = request.args.get('volume')
    mode = request.args.get('mode')
    status = request.args.get('status')
    dynamic_alsa_set(sensitivity, monitor, volume, mode, status)
    
    return jsonify(dynamic_alsa_get())
    
    
#Fade
@app.route("/api/1.0/fade/get", methods=['GET'])
def api_special_fade_get():
    return jsonify(special_fade_get())
    
@app.route("/api/1.0/fade/set", methods=['GET'])
def api_special_fade_set():
    minutes = request.args.get('minutes')
    target = request.args.get('target')
    status = request.args.get('status')
    special_fade_set(minutes, target, status)

    return jsonify(special_fade_get()) 
    
#Alarm
@app.route("/api/1.0/alarm/get", methods=['GET'])
def api_special_alarm_get():
    return jsonify(special_alarm_get())
    
@app.route("/api/1.0/alarm/set", methods=['GET'])
def api_special_alarm_set():
    time = request.args.get('time')
    lead = request.args.get('lead')
    tail = request.args.get('tail')
    status = request.args.get('status')
    special_alarm_set(time, lead, tail, status)

    return jsonify(special_alarm_get()) 


    
###HOMEBRIDGE API### 

##RGB Lamp

#Get/set status considering all modes
@app.route("/api/1.0/homebridge/rgb/<string:st>", methods=['GET'])
def set_status(st):
    
    if st == 'on': #If turned on by http
        if beast.clamp._running==False: #If RGB lamp specifically not already on
            print("Homekit turning lamp on...")
            beast.clamp.start() #Turn RGB mode on
        status = 1
            
    elif st == 'off':
        if any_running()==True: #If any mode is on
            print("Homekit turning lamp off...")
            beast.stopall() #Turn all modes off
        status = 0
            
    elif st == 'status':
        print("Homekit getting lamp status...")
        status = int(any_running()) #Set status based on any running modes
        
    return str(status)

#Get colour
@app.route("/api/1.0/homebridge/rgb/color", methods=['GET'])
def get_colour():
    rgb_current = beast.clamp.rgb  # Get current RGB from device
    br_current = global_brightness_get().get("global_brightness_val")  # Get current brightness from device
    
    hsv = list(colorsys.rgb_to_hsv(*[k/255.0 for k in rgb_current]))  # Convert current RGB to HSV
    hsv[-1] = br_current/100.0  # Replace brightness in HSV with brightness from device

    rgb_br = list(colorsys.hsv_to_rgb(*hsv))  # Convert RGB accounting for brightness back into RGB
    rgb_br = [k*255 for k in rgb_br]

    return str(rgb_to_hex(rgb_br))

#Set colour
@app.route("/api/1.0/homebridge/rgb/color/<string:c>", methods=['GET'])
def set_colour(c):

    rgb = hex_to_rgb(c)  # Get RGB data from hex input
    hsv = list(colorsys.rgb_to_hsv(*[k/255.0 for k in rgb]))  # Get HSV data from RGB
    
    # Get brightness target from HSV
    br_target = hsv[-1]*100

    # Set brightness from target
    global_brightness_set(br_target)
    
    # Calculate full brightness RGB target
    hsv[-1] = 1.0
    rgb_target = list(colorsys.hsv_to_rgb(*hsv))
    rgb_target = [k*255 for k in rgb_target]
    
    # Set color from target
    if all(c<=255 for c in rgb_target): #If all values are within RGB range
        beast.clamp.rgb = rgb_target #Update colour

    return str(rgb_to_hex(beast.clamp.rgb))
 
#Get brightness
@app.route("/api/1.0/homebridge/rgb/brightness", methods=['GET'])
def get_brightness():
    br_current = global_brightness_get().get("global_brightness_val")
    return str(br_current)

#Set brightness
@app.route("/api/1.0/homebridge/rgb/brightness/<int:b>", methods=['GET'])
def set_brightness(b):
    print("This should never actually run. I don't even know why it's here...")
    global_brightness_set(b)
    return str(int(100*beast.core.getbrightness()))
    
    
    
### EXIT AND START ROUTINES ### 
 
def emergency_shutdown():
    #Stop all running processes
    beast.stopall()
    beast.special.alarm.stop()
    beast.special.fade.stop()
    beast.core.clear()

atexit.register(emergency_shutdown)
    

#START SERVER

if __name__=='__main__':
    app.run(host='0.0.0.0', threaded=True)
