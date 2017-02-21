import unicornhat as unicorn
import math

#CORE VARIABLES
hardlimit=0.8


#CORE FUNCTIONS

def clear():
    unicorn.off()


def setall(r,g,b):
    for i in range(8):
        for j in range(8):
            unicorn.set_pixel(i, j, int(r), int(g), int(b))
    unicorn.show()


def setbrightness(brightmax): #Set maximum brightness
    global brightscale
    if 0<=brightmax<=1:
        brightscale=brightmax*hardlimit #Hard cap at global limit
        unicorn.brightness(brightscale) #Set brightness through unicornhat library
        unicorn.show()
        print "Brightness capped at ", brightscale
    else:
        print "Brightness must be between 0 and 1"

def getbrightness(pc=False): #Returns user-facing brightness as a percentage
    global hardlimit, brightscale
    if not pc:
        return round(brightscale/hardlimit,2)
    elif pc:
        return int(round(brightscale/hardlimit,2)*100)

def temptorgb(tempin):
        
    temperature = float(tempin)/100

    #Whitepoint at 6600K

    rgb=[]

    #RED
    if temperature<=66:
        red=255
    else:
        red=temperature-60
        red=329.698727446*(red**(-0.1332047592))
        if red < 0:
            red = 0
        if red > 255:
            red = 255

    #GREEN

    if temperature <= 66:
        green = temperature
        green = 99.4708025861*math.log(green) - 161.1195681661
        if green < 0:
            green = 0
        if green > 255:
            green = 255
    else:
        green = temperature - 60
        green = 288.1221695283*(green**(-0.0755148492))
        if green < 0:
            green = 0
        if green > 255:
            green = 255

    #BLUE
    if temperature >= 66:
        blue = 255
    else:
        if temperature <= 19:
            blue = 0
        else:
            blue = temperature - 10
            blue = 138.5177312231*math.log(blue) - 305.0447927307

            if blue < 0:
                blue = 0
            if blue > 255:
                blue = 255

    rgb.append(red)
    rgb.append(green)
    rgb.append(blue)

    return rgb