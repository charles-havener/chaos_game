import datashader as ds
import datashader.transfer_functions as tf
from datashader.utils import export_image

import numpy as np
from numpy import linspace

from numba import jit
from numba.typed import List

import matplotlib
from matplotlib import cm

import pandas as pd
import random
import pathlib
import os
from math import sin, cos, sqrt, fabs, pi


# Generates a random vertex based on given probabilities.
@jit(nopython=True)
def getRandVert(prob):
    return np.searchsorted(prob, random.random(), side='right')


# Creates the variables that the various rule functions will return.
@jit(nopython=True)
def getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert):
    newX = vertsX[randVert] - ((vertsX[randVert]-x)*cos(rot[randVert]*pi/180)-(
        vertsY[randVert]-y)*sin(rot[randVert]*pi/180))/comp[randVert]
    newY = vertsY[randVert] - ((vertsX[randVert]-x)*sin(rot[randVert]*pi/180)+(
        vertsY[randVert]-y)*cos(rot[randVert]*pi/180))/comp[randVert]
    prev2 = prev1
    prev1 = randVert
    return newX, newY, randVert, prev1, prev2

# -- Rule Functions --

# 1. Next point can be any of the outer points.
@jit(nopython=True)
def standard(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob):
    randVert = getRandVert(prob)
    return getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert)


# 2. Next point can be any point other than the previous chosen (i.e cannot choose point 1 twice in a row).
@jit(nopython=True)
def not_prev(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob):
    while True:
        randVert = getRandVert(prob)
        if(randVert != prev1):
            break

    return getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert)


# 3. Next point can be any point other than the one counter clockwise of the previously chosen point (i.e cannot choose point 1 if 2 was the previous point).
@jit(nopython=True)
def not_ccw(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob):
    while True:
        randVert = getRandVert(prob)
        if(randVert != (prev1-1) % len(vertsX)):
            break

    return getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert)


# 4. Next point can be any point other than the point directly clockwise of the previously chosen point (i.e cannot chose point 2 if 1 was the previous point).
@jit(nopython=True)
def not_cw(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob):
    while True:
        randVert = getRandVert(prob)
        if(randVert != (prev1+1) % len(vertsX)):
            break

    return getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert)


# 5. Next point can be any point other than the one directly opposite only applies to even sided shapes (i.e in a square cannot  go 1->3 or 2->0).
@jit(nopython=True)
def not_opposite(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob):
    while True:
        randVert = getRandVert(prob)
        if(randVert != (prev1+len(vertsX)/2) % len(vertsX)):
            break

    return getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert)


# 6. Next point can be any point other than the one to the immediate right or left of the one currently chosen (i.e in pentagon can not go 2->1 or 2->3).
@jit(nopython=True)
def not_adj(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob):
    while True:
        randVert = getRandVert(prob)
        if(randVert != (prev1-1) % len(vertsX)) and (randVert != (prev1+1) % len(vertsX)):
            break

    return getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert)


# 7. Next point can be any point other than the one to the immediate right or left of the 2 previous chosen (i.e in pentagon, if two previous were 0 and 4, next point must be 2).
@jit(nopython=True)
def not_adj_prev2(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob):
    while True:
        randVert = getRandVert(prob)
        if(randVert != (prev1-1) % len(vertsX)) and (randVert != (prev1+1) % len(vertsX)) and (randVert != (prev2-1) % len(vertsX)) and (randVert != (prev2+1) % len(vertsX)):
            break

    return getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert)


# 8. Next point cannot be adjacent to the previously chosen point if the two previous points are the same.
# (i.e if previous two points were both 3, next point cannot be 2 or 4, if the previous two points are different, any next point is valid).
@jit(nopython=True)
def not_adj_prev2_same(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob):
    if prev1 == prev2:
        while True:
            randVert = getRandVert(prob)
            if(randVert != (prev1-1) % len(vertsX)) and (randVert != (prev1+1) % len(vertsX)):
                break
    else:
        randVert = getRandVert(prob)

    return getReturn(x, y, prev1, prev2, vertsX, vertsY, comp, rot, prob, randVert)

# -- End Rules --


# Reformats the inputs to jit usable form.
def getInputList(input, numV, default):
    tmp = input
    ret = List()
    if isinstance(input, list):
        input = [float(x) for x in input]
        if len(input) < numV:
            for i in range(len(input), numV):
                input.append(default)

    else:
        if isinstance(input, float) or isinstance(input, int):
            input = np.zeros(numV)
            for i in range(numV):
                input[i] = tmp
        else:
            input = np.zeros(numV)
            for i in range(numV):
                input[i] = default

    [ret.append(x) for x in input]
    return ret


# Generates the (x,y) locations and categories for n points.
@jit(nopython=True)
def trajectory_coords(fn, numV, comp, rot, prob, n):
    x, y, c, vertsX, vertsY = np.zeros(n), np.zeros(
        n), np.zeros(n), np.zeros(numV), np.zeros(numV)

    for i in np.arange(numV):
        vertsX[i] = cos(i*2*pi/numV)
        vertsY[i] = sin(i*2*pi/numV)

    c[0] = 0
    x[0], y[0] = vertsX[0], vertsY[0]
    prev1, prev2 = 0, 0

    for i in np.arange(n-1):
        x[i+1], y[i+1], c[i+1], prev1, prev2 = fn(
            x[i], y[i], prev1, prev2, vertsX, vertsY, comp, rot, prob)
    return x, y, c


# Returns points and their categories in a dataframe.
def trajectory(fn, numV, comp, rot, prob, n):
    x, y, c = trajectory_coords(fn, numV, comp, rot, prob, n)
    return pd.DataFrame(dict(x=x, y=y, c=c))


# Creates the image
def createImage(n, numV, comp, rot, prob, rule, colorMap, location, dims, redMethod):

    # Lets ruleIndex be passed to trajectory to call a function rather than as a string which is received.
    ruleSet = [standard, not_prev, not_ccw, not_cw,
               not_opposite, not_adj, not_adj_prev2, not_adj_prev2_same]
    ruleSetStrings = ['standard', 'not_prev', 'not_ccw',
                      'not_cw', 'not_opposite', 'not_adj', 'not_adj_prev2', 'not_adj_prev2_same']
    ruleIndex = ruleSetStrings.index(rule)

    # gets evenly distributed colors from the chosen colorMap.
    if colorMap == "all white":
        colors = [matplotlib.colors.to_hex(
            (1, 1, 1)) for x in linspace(0.0, 1.0, numV)]
    elif colorMap == "focus one":
        colors = [matplotlib.colors.to_hex(
            (0, 0, 0)) for x in linspace(0.0, 1.0, numV)]
        colors[0] = matplotlib.colors.to_hex((1, 1, 1))
    else:
        colors = [matplotlib.colors.to_hex(cm.get_cmap(colorMap)(
            x), keep_alpha=False) for x in linspace(0.0, 1.0, numV)]
        print(colors[0], type(colors[0]))

    # Puts compression, rotation, and probability inputs into a jit usable format.
    defaults = [2, 0, 1/numV]
    comp = getInputList(comp, numV, defaults[0])
    rot = getInputList(rot, numV, defaults[1])

    # Each element in prob becomes cumulative sum of elements before. Then scales elements so total sum is 1.
    prob = np.cumsum(getInputList(prob, numV, defaults[2]))
    probSum = prob[-1]
    for x in range(numV):
        prob[x] *= (1/probSum)

    # Generates points and designates a category field.
    df = trajectory(ruleSet[ruleIndex], numV, comp, rot, prob, int(n))
    df['c'] = df['c'].astype("category")

    # Find the point range to get optimal plot size for image.
    xm, xs, ym, ys = df['x'].max(), df['x'].min(), df['y'].max(), df['y'].min()
    max_range = max(xm-xs, ym-ys)
    x_range = ((xm+xs)/2-(max_range)/2, (xm+xs)/2+(max_range)/2)
    y_range = ((ym+ys)/2-(max_range)/2, (ym+ys)/2+(max_range)/2)

    #  Create the canvas with optimal dimensions found above.
    cvs = ds.Canvas(plot_width=dims,
                    plot_height=dims,
                    x_range=x_range, y_range=y_range)

    # Aggregates points using chosen reduction method.
    if redMethod == "Line":
        agg = cvs.line(df, 'x', 'y', agg=ds.by('c', ds.count()))
    else:
        agg = cvs.points(df, 'x', 'y', agg=ds.by('c', ds.count()))

    # Creates the image.
    ds.transfer_functions.Image.border = 0
    img = tf.shade(agg, color_key=colors)

    # Saves the image.
    export_image(img, os.path.join(location, "image" + str(dims)))

    # Outputs to console where the image was saved at.
    print("\tImage saved at " +
          str(pathlib.Path(__file__).parent.absolute()) + "\\" + "image" + str(dims) + ".png")

    return 0