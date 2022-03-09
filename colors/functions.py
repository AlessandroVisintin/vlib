import numpy as np
from skimage import color


# input:#hex output:(r,g,b)
def hex2rgb(h):
        return (int(h[1:3],16), int(h[3:5],16), int(h[5:7],16))


# input:(r,g,b) output:#hex 
def rgb2hex(r):
    r = [int(round(x)) for x in r]
    return f'#{r[0]:02x}{r[1]:02x}{r[2]:02x}'


# input:(r,g,b) output:lab
def rgb2lab(r):
    return color.rgb2lab([np.array(r, dtype='uint8')])[0]


def lab2rgb(l):
    return np.array(color.lab2rgb(l) * 255, dtype='uint8')


# input:(r,g,b) output:relative luminance
def relative_luminance(r):
    Rs, Gs, Bs  = np.array(r) / 255
    R = Rs / 12.92 if Rs <= 0.03928 else ((Rs + 0.055) / 1.055)**2.4
    G = Gs / 12.92 if Gs <= 0.03928 else ((Gs + 0.055) / 1.055)**2.4
    B = Bs / 12.92 if Bs <= 0.03928 else ((Bs + 0.055) / 1.055)**2.4
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


# input::(r,g,b) output:contrast between colors
def contrast(rgb1, rgb2):
    l1, l2 = (relative_luminance(rgb1), relative_luminance(rgb2)) 
    if l1 > l2:
        return (l1 + 0.05) / (l2 + 0.05)
    return (l2 + 0.05) / (l1 + 0.05)


# input: (r,g,b), int output: fade from rgb1 to rgb2 in steps
def interpolate(rgb1, rgb2, steps):
    lab1, lab2 = color.rgb2lab([np.array([rgb1, rgb2], dtype='uint8')])[0]
    dlab = lab2 - lab1
    out = [lab1 + dlab*i for i in [i / (steps-1) for i in range(steps)]]
    out = np.array(color.lab2rgb([out])[0] * 255, dtype='uint8')
    return [tuple(x) for x in out]
