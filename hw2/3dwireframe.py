#!/usr/bin/python

import pyparsing as pp
import sys
import os
import numpy as np
from math import*

def rotationMatrix(a, b, c, theta):
    return np.array([[a**2 + (1 - a**2)*cos(theta), a*b*(1-cos(theta)) - c*sin(theta), a*c*(1-cos(theta)) + b*sin(theta), 0],
	                    [a*b*(1-cos(theta)) + c*sin(theta), b**2 + (1-b**2)*cos(theta), b*c*(1-cos(theta)) - a*sin(theta), 0],
	                    [a*c*(1-cos(theta)) - b*sin(theta), b*c*(1-cos(theta)) + a*sin(theta), c**2 + (1-c**2)*cos(theta), 0],
	                    [0, 0, 0, 1]])

def translateMatrix(a, b, c):
    return translateMat = np.array([[1, 0, 0, a], 
                                    [0, 1, 0, b], 
                                    [0, 0, 1, c], 
                                    [0, 0, 0, 1]])

fo = sys.stdin

# define grammar
# number is float form
number = pp.Regex(r"-?\d+(\.\d*)?([Ee][+-]?\d+)?")
number.setParseAction(lambda toks:float(toks[0]))

leftBrace = pp.Literal("{")
rightBrace = pp.Literal("}")
leftBracket = pp.Literal("[")
rightBracket = pp.Literal("]")
comma = pp.Literal(",")

# Optional added for the additional number for rotation
parameter = pp.Optional(pp.Word( pp.alphas )) + pp.Optional(leftBrace) + \
	        pp.Optional(rightBrace) + pp.Optional(number) + pp.Optional(comma) + \
            pp.Optional(number) + pp.Optional(comma) + pp.Optional(number) + \
            pp.Optional(comma) + pp.Optional(number)

# split the text between file name and file extension
fileName, fileExtension = os.path.splitext(os.readlink('/proc/self/fd/0'))

first = fo.readline()

# as long as we don't reach the end of the file
while (first != ''):
    firstparse = parameter.parseString(first)
    print firstparse

    # if we reach PerspectiveCamera parameter
    if (len(firstparse) != 0 and (firstparse[0] == 'PerspectiveCamera')):
        first = fo.readline()
        # if there is a blank line, read another main parameter
        while (first.strip() != ''):
            firstparse = parameter.parseString(first)

            # position parameter
            if (firstparse[0] == 'position'):
                translateX = firstparse[1]
                translateY = firstparse[2]
                translateZ = firstparse[3]

            # orientation paramter
            elif (firstparse[0] == 'orientation'):
                x = firstparse[1]
                y = firstparse[2]
                z = firstparse[3]
                angle = firstparse[4]

            # near distance parameter
            elif (firstparse[0] == 'nearDistance'):
                n = firstparse[1]

            # far distance paramter
            elif (firstparse[0] == 'farDistance'):
                f = firstparse[1]
    
            # left parameter
            elif (firstparse[0] == 'left'):
                l = firstparse[1]

            # right parameter
            elif (firstparse[0] == 'right'):
                r = firstparse[1]
        
            # bottom parameter
            elif (firstparse[0] == 'bottom'):
                b = firstparse[1]

            # top parameter
            elif (firstparse[0] == 'top'):
                t = firstparse[1]
            first = fo.readline()

    # if we reach the Separator parameter
    if (len(firstparse) != 0 and (firstparse[0] == 'Separator')):
        first = fo.readline()
        firstparse = parameter.parseString(first)
        
        # if we reach the Transform sub-parameter
        if (len(firstparse) != 0 and (firstparse[0] == 'Transform')):
            first = fo.readline()
            firstparse = parameter.parseString(first)
            
            # as long as we aren't at the end of the Transform parameter
            while (firstparse[0] != '}'):

                # translation
                if (firstparse[0] == 'translation'):
                    print "wut"
                    tX = firstparse[1]
                    tY = firstparse[2]
                    tZ = firstparse[3]
                elif (firstparse[0] == 'rotation'):
                    rX = firstparse[1]
                    rY = firstparse[2]
                    rZ = firstparse[3]
                    rAngle = firstparse[4]

                else:
                    sfX = firstparse[1]
                    sfY = firstparse[2]
                    sfZ = firstparse[3]
                first = fo.readline()
                firstparse = parameter.parseString(first)
    first = fo.readline()

# translation matrix
translateCam = translateMatrix(translateX, translateY, translateZ)

# rotation matrix
rotationCam = rotationMatrix(x, y, z, angle)

# calculate the camera matrix
# World space to camera space
cameraMat = np.dot(translateCam, rotationCam)


# calculate the Perspective Projection matrix
perspectiveProj = np.array([[2.0*n / (r - l), 0, float(r + l)/(r - l), 0], 
                            [0, 2.0*n / (t - b), float(t + b) / (t - b), 0],
                            [0, 0, -1.0*(f + n)/(f - n), -2.0*(f*n)/(f - n)],
                            [0, 0, -1, 0]])

print perspectiveProj