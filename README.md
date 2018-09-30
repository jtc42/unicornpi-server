# unicornpi-server
Pi-side codebase for [Pimoroni Unicorn HAT](https://shop.pimoroni.com/products/unicorn-hat) remote control.

A blog post detailing the basic functionality can be found [here](https://medium.com/@jtcollins/the-worlds-most-over-engineered-lamp-fc22cd65ae88). I suggest reading this first to get an idea of what to expect.

Once everything is set up, you can use either a web browser on your local network, or the [Android app](https://github.com/jtc42/unicornpi-android) to control the LEDs.

## Requirements
* Python >3.5
* [Unicorn HAT library](https://github.com/pimoroni/unicorn-hat)
* [Python Flask](http://flask.pocoo.org/)
* [Pyalsaaudio](https://pypi.python.org/pypi/pyalsaaudio) (Optional)

## Getting started
* Clone or download the files from here
* On the Pi, navigate to the download location, and run 'sudo python main.py'

*Note: sudo is required to run the Unicorn HAT*

*I also strongly reccommend using [Linux Screen](https://www.howtoforge.com/linux_screen) to do this, as it allows you to check back on the console output remotely, or after closing the console used to launch.*

* The Flask server should start on the default port (5000)
* If you have a .local address set up for your Pi, this can be used to access the server

### API
* I have implemented a web API that allows sending commands to the server through HTTP-get requests, and returns system status as returned JSON.
* I've made a document detailing basic functionality, found [here](https://docs.google.com/document/d/1qIMybzcNMx6zFvN5bqxL-kA0C5EpSCOA15KcieoZDWU/edit?usp=sharing).
* So far this is primarliy used in the Android app I've made to control the device. The app can be found [here.](https://github.com/jtc42/unicornpi-android)

## Notes on ALSA graphic equalizer
* **In Python 3, ALSA is entirely untested and likely very broken. I'll try and get round to fixing it soon.**
* The ALSA integration is still buggy. The idea here is that the HAT will display a graphic EQ for any audio passed to a compatible cards line-in.
* If a compatible card is detected, it will attempt to set up the graphic EQ, and enable the option in the web UI and API.
* If no card is detected, the script **should** elegantly ignore this part.
* The script makes no effort to pass audio back out through the line-out. Most cards have an option to enable pass-through, or monitoring, through the standard settings. This works on some cards I've tried, but not all.
* If you have any issues with this, feel free to mention it in the issues tracker, but be aware there's a good chance it won't work nicely.
