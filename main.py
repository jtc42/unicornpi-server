import os
import colorsys
import logging

import atexit

from flask import Flask, request, make_response, jsonify

DEVICE = 'UNICORN_HAT'

if DEVICE == 'UNICORN_HAT':
    from beastbox.unicorn import UnicornLamp
    lamp = UnicornLamp(correction=[1., 0.8, 1.0])
elif DEVICE == "MOTE_PHAT":
    from beastbox.motephat import MotePhatLamp
    lamp = MotePhatLamp(correction=[1., .4, .6])
elif DEVICE == "MOTE_USB":
    from beastbox.mote import MoteLamp
    lamp = MoteLamp(correction=[1., 0.5, .8])

app = Flask(__name__)

# Catch all exceptions (eg invalid arguments raising exceptions in modules)
@app.errorhandler(Exception)
def all_exception_handler(e):
    logging.error(e)
    return make_response(jsonify({'error': str(e)}), 500)

# API
@app.route("/api", methods=['GET', 'POST'])
def api_state():
    if request.method == 'POST':
        payload = request.get_json()

        logging.debug(payload)

        lamp.set_representation(payload)

    return jsonify(lamp.get_representation())


### EXIT AND START ROUTINES ### 
 
def emergency_shutdown():
    #Stop all running processes
    lamp.clear()

atexit.register(emergency_shutdown)
    

#START SERVER

if __name__=='__main__':
    app.run(host='0.0.0.0', threaded=True)
