import unicornhat as unicorn
import math

#GLOBAL VARIABLES
user_brightness = 0.0

#CORE FUNCTIONS

def clear():
    unicorn.off()


def setall(r,g,b):
    for i in range(8):
        for j in range(8):
            unicorn.set_pixel(i, j, int(r), int(g), int(b))
    unicorn.show()


def setbrightness(br): # Set maximum brightness
    global user_brightness
    if 0<=br<=1:
        user_brightness = br # Log user-selected brightness to a variable
        unicorn.brightness(br) # Set brightness through unicornhat library
        unicorn.show()
        print("Brightness capped at ", br)
    else:
        print("Brightness must be between 0 and 1")


def getbrightness(pc=False): # Returns user-facing brightness as a percentage
    if not pc:
        return user_brightness # Return stored user-selected brightness
    elif pc:
        return int(user_brightness*100) # Return stored user-selected brightness * 100


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