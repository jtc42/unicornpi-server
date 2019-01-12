from beastbox.unicorn import UnicornLamp
import os
import colorsys
from pprint import pprint

import atexit
from beastbox.utilities import hex_to_rgb, rgb_to_hex

from flask import Flask, request, make_response, jsonify

### SETUP ###
CATCHEXCEPTIONS = False
DEBUG = False

lamp = UnicornLamp()


###FLASK###

#Initial Setup
app = Flask(__name__)
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

        lamp.set_state(payload)

    response = lamp.state
    print("\nRESPONSE:")
    pprint(response)
    return jsonify(response)

    
### EXIT AND START ROUTINES ### 
 
def emergency_shutdown():
    #Stop all running processes
    lamp.alarm.stop()
    lamp.fade.stop()
    lamp.stop()

atexit.register(emergency_shutdown)
    

#START SERVER

if __name__=='__main__':
    app.run(host='0.0.0.0', threaded=True)
