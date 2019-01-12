import math

def fuzzybool(val):
    fuzzytrues = ["1", 1, True, "True", "true"]
    if val in fuzzytrues:
        return True
    else:
        return False

def hex_to_rgb(value):
    h = value.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def rgb_to_hex(rgb):
    rgb=tuple(rgb)
    return '%02x%02x%02x' % rgb

def temptorgb(tempin):

    temperature = float(tempin) / 100

    # Whitepoint at 6600K

    rgb = []

    # RED
    if temperature <= 66:
        red = 255
    else:
        red = temperature - 60
        red = 329.698727446 * (red**(-0.1332047592))
        if red < 0:
            red = 0
        if red > 255:
            red = 255

    # GREEN

    if temperature <= 66:
        green = temperature
        green = 99.4708025861 * math.log(green) - 161.1195681661
        if green < 0:
            green = 0
        if green > 255:
            green = 255
    else:
        green = temperature - 60
        green = 288.1221695283 * (green**(-0.0755148492))
        if green < 0:
            green = 0
        if green > 255:
            green = 255

    # BLUE
    if temperature >= 66:
        blue = 255
    else:
        if temperature <= 19:
            blue = 0
        else:
            blue = temperature - 10
            blue = 138.5177312231 * math.log(blue) - 305.0447927307

            if blue < 0:
                blue = 0
            if blue > 255:
                blue = 255

    rgb.append(red)
    rgb.append(green)
    rgb.append(blue)

    return rgb
