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
    return np.array([[1, 0, 0, a], 
                    [0, 1, 0, b], 
                    [0, 0, 1, c], 
                    [0, 0, 0, 1]])

def scalefactorMatrix(a, b, c):
    return np.array([[a, 0, 0, 0], 
                   [0, b, 0, 0], 
                   [0, 0, c, 0], 
                   [0, 0, 0, 1]])

# regular bresenham, for positive slopes between 0 and 1.
def bresenham(a1, b1, a2, b2, xlen, ylen):
    y = b1
    dy = b2 - b1
    dxdy = b2 - b1 + a1 - a2
    F = b2 - b1 + a1 - a2
    print "the coordinates of 1st point are: (", a1, ", ", b1, ")"
    print "the coordinates of 2nd point are: (", a2, ", ", b2, ")"
    for i in range(a1, a2 + 1):
        index = (int(ylen/2) - y - 1)*xlen + i + int(xlen/2) - 1
        # index cannot be outside of pixel array and we cannot go back one row by subtracting
        if (index < xlen * ylen and i + int(xlen/2) - 1 > 0):
            pixel[index] = 1
        if(F < 0):
            F += dy
        else:
            y += 1
            F += dxdy
    return

# using the algorithm for pixel that (xlen - x)*xlen + (ylen - y)
# for positive slopes greater than 1
def bresenhamG1(a1, b1, a2, b2, xlen, ylen):
    y = a1
    dy = a2 - a1
    dxdy = a2 - a1 + b1 - b2
    F = a2 - a1 + b1 - b2
    print "the coordinates of 1st point G1 are: (", a1, ", ", b1, ")"
    print "the coordinates of 2nd point G1 are: (", a2, ", ", b2, ")"
    for i in range(b1, b2 + 1):
        index = (int(xlen/2) - i - 1)*xlen + (y + int(ylen/2)) - 1
        # index cannot be outside of pixel array and we cannot go back one row by subtracting
        if (index < xlen * ylen and (y + int(ylen/2)) - 1 > 0):
            pixel[index] = 1
        if(F < 0):
            F += dy
        else:
            y += 1
            F += dxdy
    return

# using the algorithm to flip over the y-axis, and do the bresenham algorithm
# then, flip back to correct pixel form by subtracting xlen - (i + xlen/2)
# for negative slopes between -1 and 0
def bresenhamNeg(a1, b1, a2, b2, xlen, ylen):
    y = b2
    dy = b1 - b2
    dxdy = b1 - b2 + a1 - a2
    F = b1 - b2 + a1 - a2
    print "the coordinates of 1st point neg are: (", a1, ", ", b1, ")"
    print "the coordinates of 2nd point neg are: (", a2, ", ", b2, ")"
    for i in range(-1*a2, -1*a1 + 1):
        # minus 1 because of it starts at 0
        index = (int(ylen/2) - y - 1)*xlen + int(xlen/2) - i - 1
        # index cannot be outside of pixel array and we cannot go back one row by subtracting
        if (index < xlen * ylen and int(xlen/2) - i - 1 > 0):
            pixel[index] = 1
        if(F < 0):
            F += dy
        else:
            y += 1
            F += dxdy
    return

# using the algorithm for pixel that (xlen - x)*xlen + (ylen - y)
# for negative slopes less than -1
def bresenhamNegG1(a1, b1, a2, b2, xlen, ylen):
    y = -1*a2
    dy = a2 - a1
    dxdy = a2 - a1 + b2 - b1
    F = a2 - a1 + b2 - b1
    print "the coordinates of 1st point negG1 are: (", a1, ", ", b1, ")"
    print "the coordinates of 2nd point negG1 are: (", a2, ", ", b2, ")"
    for i in range(b2, b1 + 1):
        index = (int(xlen/2) - i - 1)*xlen + int(ylen/2) - y - 1
        # index cannot be outside of pixel array and we cannot go back one row by subtracting
        if (index < xlen * ylen and ylen/2 - y - 1 > 0):
            pixel[index] = 1
        if(F < 0):
            F += dy
        else:
            y += 1
            F += dxdy
    return

fo = sys.stdin

# x dimension size
xRes = int(sys.argv[1])

# y dimension size
yRes = int(sys.argv[2])

# define grammar
# number is float form
# does +/-, 0., .2, and exponentials
number = pp.Regex(r"[-+]?([0-9]*\.[0-9]*|[0-9]+)([Ee][+-]?[0-9]+)?")
number.setParseAction(lambda toks:float(toks[0]))

leftBrace = pp.Literal("{")
rightBrace = pp.Literal("}")
leftBracket = pp.Literal("[")
rightBracket = pp.Literal("]")
comma = pp.Literal(",")

# Optional added for the additional number for rotation
parameter = pp.Optional(pp.Word( pp.alphas )) + pp.Optional(leftBracket) + \
            pp.Optional(leftBrace) + pp.Optional(rightBracket) + \
	        pp.Optional(rightBrace) + pp.ZeroOrMore(number + pp.Optional(comma))

# make a list of all the pixels of the window
pixel = [0]*xRes*yRes

# split the text between file name and file extension
fileName, fileExtension = os.path.splitext(os.readlink('/proc/self/fd/0'))

# create the ppm file
ppm = open(fileName + ".ppm", "w")
ppm.write("P3 \n")
ppm.write(str(xRes) + " " + str(yRes) + "\n")
ppm.write(str(255) + "\n")

first = fo.readline()

# as long as we don't reach the end of the file
while (first != ''):
    firstparse = parameter.parseString(first)

    # if we reach PerspectiveCamera parameter
    if (len(firstparse) != 0 and (firstparse[0] == 'PerspectiveCamera')):
        first = fo.readline()
        # if there is a blank line, read another main parameter
        while (first.strip() != ''):
            firstparse = parameter.parseString(first)
            print firstparse
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
                print "the params are: ", y

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

        # translation matrix (for position of camera)
        translateCam = translateMatrix(translateX, translateY, translateZ)

        # rotation matrix (for orientation of camera)
        rotationCam = rotationMatrix(x, y, z, angle)

        # calculate the camera matrix
        # World space to camera space
        cameraMat = np.dot(translateCam, rotationCam)

        # calculate the Perspective Projection matrix
        perspectiveProj = np.array([[2.0*n / (r - l), 0, float(r + l)/(r - l), 0], 
                                    [0, 2.0*n / (t - b), float(t + b) / (t - b), 0],
                                    [0, 0, -1.0*(f + n)/(f - n), -2.0*(f*n)/(f - n)],
                                    [0, 0, -1, 0]])


    # if we reach PointLight parameter
    while (len(firstparse) != 0 and (firstparse[0] == 'PointLight')):
        first = fo.readline()
        # if there is a blank line, read another main parameter
        while (first.strip() != ''):
            firstparse = parameter.parseString(first)
            # location parameter
            if (firstparse[0] == 'location'):
                lightX = firstparse[1]
                lightY = firstparse[2]
                lightZ = firstparse[3]
            # color parameter
            elif (firstparse[0] == 'color'):
                red = firstparse[1]
                green = firstparse[2]
                blue = firstparse[3]
            first = fo.readline()
        first = fo.readline()
        firstparse = parameter.parseString(first)
        print "the colors are: ", red, ", ", green, ", ", blue

    # if we reach the Separator parameter
    while (len(firstparse) != 0 and (firstparse[0] == 'Separator')):
        first = fo.readline()
        firstparse = parameter.parseString(first)
        
        # transform multiplication, initialized to identity matrix
        totaltransform = totalNorm = np.array([[1.0, 0.0, 0.0, 0.0],
                                              [0.0, 1.0, 0.0, 0.0],
                                              [0.0, 0.0, 1.0, 0.0],
                                              [0.0, 0.0, 0.0, 1.0]])

        # if we reach the Transform sub-parameter
        while (len(firstparse) != 0 and (firstparse[0] == 'Transform')):
            first = fo.readline()
            firstparse = parameter.parseString(first)
            
            translate = rotate = scaleFactor = ''
            # as long as we aren't at the end of the Transform parameter
            while (firstparse[0] != '}'):

                # translation
                if (firstparse[0] == 'translation'):
                    translate = firstparse[0]
                    tX = firstparse[1]
                    tY = firstparse[2]
                    tZ = firstparse[3]
                    translateSep = translateMatrix(tX, tY, tZ)
                # rotation
                elif (firstparse[0] == 'rotation'):
                    rotate = firstparse[0]
                    rX = firstparse[1]
                    rY = firstparse[2]
                    rZ = firstparse[3]
                    rAngle = firstparse[4]
                    rotationSep = rotationMatrix(rX, rY, rZ, rAngle)
                # scale factor
                elif (firstparse[0] == 'scaleFactor'):
                    scaleFactor = firstparse[0]
                    sfX = firstparse[1]
                    sfY = firstparse[2]
                    sfZ = firstparse[3]
                    scalefactorSep = scalefactorMatrix(sfX, sfY, sfZ)
                first = fo.readline()
                firstparse = parameter.parseString(first)

            # calculate the separator matrix (S = TRS)
            # it is for Object Space to World Space

            if (translate == '' and rotate == 'rotation' and scaleFactor == ''):
                S = rotationSep
                normS = rotationSep
            elif (translate == 'translation' and rotate == '' and scaleFactor == ''):
                S = translateSep
                normS = np.array([[1.0, 0.0, 0.0, 0.0],
                                  [0.0, 1.0, 0.0, 0.0],
                                  [0.0, 0.0, 1.0, 0.0],
                                  [0.0, 0.0, 0.0, 1.0]])
            elif (translate == '' and rotate == '' and scaleFactor == 'scaleFactor'):
                S = scalefactorSep
                normS = scalefactorSep
            elif (translate == 'translation' and rotate == 'rotation' and scaleFactor == ''):
                S = np.dot(translateSep, scalefactorSep)
                normS = rotationSep
            elif (translate == 'translation' and rotate == '' and scaleFactor == 'scaleFactor'):
                S = np.dot(translateSep, scalefactorSep)
                normS = scalefactorSep
            elif (translate == '' and rotate == 'rotation' and scaleFactor == 'scaleFactor'):
                S = np.dot(rotationSep, scalefactorSep)
                normS = np.dot(rotationSep, scalefactorSep)
            elif (translate == 'translation' and rotate == 'rotation' and scaleFactor == 'scaleFactor'):
                SIntermediate = np.dot(rotationSep, scalefactorSep)
                S = np.dot(translateSep, SIntermediate)
                normS = np.dot(rotationSep, scalefactorSep)

            # Multiply up the transform matrices
            totaltransform = np.dot(totaltransform, S)

            totalNorm = np.dot(totalNorm, normS)

            # end of Transform block parameter
            if (len(firstparse) != 0 and (firstparse[0] == '}')):
                first = fo.readline()
                firstparse = parameter.parseString(first)

            # calculate camera space to NDC (Normalized Device Coordinate) Space
            transformInter = np.dot(perspectiveProj, np.linalg.inv(cameraMat))
            transformMat = np.dot(transformInter, totaltransform)

            # calculate normal transformation matrix
            normTransform = np.transpose(np.linalg.inv(totalNorm))

        # entering the Material subparameter
        if (len(firstparse) != 0 and (firstparse[0] == 'Material')):
            first = fo.readline()
            # if there is a blank line, read another main parameter
            while (first.strip() != '}'):
                firstparse = parameter.parseString(first)
                print "hmmm", firstparse
                # ambient color parameter
                if (firstparse[0] == 'ambientColor'):
                    ambX = firstparse[1]
                    ambY = firstparse[2]
                    ambZ = firstparse[3]
                # diffuse color parameter
                elif (firstparse[0] == 'diffuseColor'):
                    diffX = firstparse[1]
                    diffY = firstparse[2]
                    diffZ = firstparse[3]
                # specular color parameter
                elif (firstparse[0] == 'specularColor'):
                    specX = firstparse[1]
                    specY = firstparse[2]
                    specZ = firstparse[3]
                # diffuse color parameter
                elif (firstparse[0] == 'shinines'):
                    shiny = firstparse[1]
                first = fo.readline()
            first = fo.readline()
            firstparse = parameter.parseString(first)
        while (first.strip() == ''):
            first = fo.readline()
            firstparse = parameter.parseString(first)

        # entering the Coordinate subparameter
        if (len(firstparse) != 0 and (firstparse[0] == 'Coordinate')):
            first = fo.readline()
            firstparse = parameter.parseString(first)
            if (len(firstparse) != 0 and (firstparse[0] == 'point')):
                # Create a list of the coordinates
                coordsList = []
                # to compensate for the point
                f = 2
                while (firstparse[f] != ']' and firstparse[f] != '}' and first.strip() != '}'):
                    xArr = float(firstparse[f])
                    yArr = float(firstparse[f+1])
                    zArr = float(firstparse[f+2])

                    newmat = np.dot(transformMat, np.array( [[xArr], 
                                                             [yArr], 
                                                             [zArr], 
                                                             [1.0]] ))
                    newX = newmat[0,0]/newmat[3,0]
                    newY = newmat[1,0]/newmat[3,0]
                    newZ = newmat[2,0]/newmat[3,0]
                    coordsList.append(newX)
                    coordsList.append(newY)
                    coordsList.append(newZ)
                    first = fo.readline()
                    firstparse = parameter.parseString(first)
                    f = 0
            first = fo.readline()
            firstparse = parameter.parseString(first)
        while (first.strip() == ''):
            first = fo.readline()
            firstparse = parameter.parseString(first)

        # end of Coordinates block parameter
        if (len(firstparse) != 0 and (firstparse[0] == '}')):
            first = fo.readline()
            firstparse = parameter.parseString(first)

        print "the coords list is: ", coordsList
        print "the length is: ", len(coordsList)

        # entering the Normal subparameter
        if (len(firstparse) != 0 and (firstparse[0] == 'Normal')):
            first = fo.readline()
            firstparse = parameter.parseString(first)
            if (len(firstparse) != 0 and (firstparse[0] == 'vector')):
                print "wut wut wut wtu wut"
                # Create a list of the coordinates
                vectorsList = []
                # to compensate for the point
                f = 2
                while (firstparse[f] != ']' and firstparse[f] != '}' and first.strip() != '}'):
                    xVec = float(firstparse[f])
                    yVec = float(firstparse[f+1])
                    zVec = float(firstparse[f+2])

                    normNew = np.dot(normTransform, np.array( [[xVec], 
                                                               [yVec], 
                                                               [zVec], 
                                                               [1.0]] ))
                    normX = normNew[0,0]/normNew[3,0]
                    normY = normNew[1,0]/normNew[3,0]
                    normZ = normNew[2,0]/normNew[3,0]
                    vectorsList.append(normX)
                    vectorsList.append(normY)
                    vectorsList.append(normZ)
                    first = fo.readline()
                    firstparse = parameter.parseString(first)
                    f = 0
            first = fo.readline()
            firstparse = parameter.parseString(first)
        while (first.strip() == ''):
            first = fo.readline()
            firstparse = parameter.parseString(first)

        # end of Coordinates block parameter
        if (len(firstparse) != 0 and (firstparse[0] == '}')):
            first = fo.readline()
            firstparse = parameter.parseString(first)

        # start into the IndexedFaceSet block parameter
        if (len(firstparse) != 0 and (firstparse[0] == 'IndexedFaceSet')):
            first = fo.readline()

            # to determine which vertices to render
            polygonvertices = []
            toRender = []
            # read until the end of the IndexedFaceSet block parameter
            while(first.strip() != '}'):
                firstparse = parameter.parseString(first)

                # for the first row, with the coordIndex as firstparse[0]
                i = 0
                print "wtf"
                # Go through the line
                while (i < len(firstparse) and firstparse[0] != 'normalIndex'):
                    k = firstparse[i]
                    # if the element is a comma, bracket, or coordIndex, then move on to next element
                    while ((k == ',') or (k == '[') or (k == ']') or (k == 'coordIndex')):
                        if (i < len(firstparse) - 1):
                            i += 1
                            k = firstparse[i]
                        else:
                            first = fo.readline()
                            firstparse = parameter.parseString(first)
                            i = 0
                            k = firstparse[i]
                        
                    # put the 1st point in x1, y1
                    # multiply by 1.0/2.0 because the origin is in the center of the window
                    if (k != -1):
                        x1 = coordsList[int(3*k)]
                        y1 = coordsList[int(3*k) + 1]
                        z1 = coordsList[int(3*k) + 2]
                        polygonvertices.append(x1)
                        polygonvertices.append(y1)
                        polygonvertices.append(z1)
                    else:
                        #print polygonvertices
                        #print "the number of points is: ", len(polygonvertices)/2
                        j = 3
                        while (j < len(polygonvertices) - 5):
                            rbackcull = np.array([polygonvertices[0], polygonvertices[1], polygonvertices[2]])
                            sbackcull = np.array([polygonvertices[j], polygonvertices[j+1], polygonvertices[j+2]])
                            tbackcull = np.array([polygonvertices[j+3], polygonvertices[j+4], polygonvertices[j+5]])

                            a = np.cross(rbackcull - sbackcull, sbackcull - tbackcull)
                            #print rbackcull
                            #print a
                            if (j == 3 and a[2] > 0):
                                toRender.append(rbackcull[0])
                                toRender.append(rbackcull[1]) 
                                toRender.append(sbackcull[0])
                                toRender.append(sbackcull[1])
                                toRender.append(tbackcull[0])
                                toRender.append(tbackcull[1])
                            elif (j > 3 and a[2] > 0):
                                toRender.append(tbackcull[0])
                                toRender.append(tbackcull[1])
                            j += 3
                        if (len(toRender) > 0 and toRender[-1] != -1):
                            toRender.append(-1)
                        polygonvertices = []

                    i += 1
                print toRender

                # Read through the polygons and points to render
                x1 = int(toRender[0] * xRes * 1.0/2.0)
                y1 = int(toRender[1] * yRes * 1.0/2.0)
                h = 2
                while (h < len(toRender)):
                    if (toRender[h] == -1):
                        # wrap around 
                        c1 = a2
                        d1 = b2
                        c2 = x1
                        d2 = y1

                        # Apply Bresenham's line algorithm
                        if (c2 <= c1):            
                            m1 = c2
                            n1 = d2
                            m2 = c1
                            n2 = d1
                        else:
                            m1 = c1
                            n1 = d1
                            m2 = c2
                            n2 = d2
                        # for the case where the positive slope <= 1 
                        if((n2 - n1 >= 0) and (m2 - m1 >= n2 - n1)):
                            bresenham(m1, n1, m2, n2, xRes, yRes)

                        # for the case where the positive slope > 1
                        elif((n2 - n1 >= 0) and (m2 - m1 < n2 - n1)):
                            bresenhamG1(m1, n1, m2, n2, xRes, yRes)

                        # for the case where the negative slope >= -1
                        elif((n2 - n1 < 0) and (m2 - m1 >= n1 - n2)):
                            bresenhamNeg(m1, n1, m2, n2, xRes, yRes)

                        # for the case where the negative slope < -1
                        elif((n2 - n1 < 0) and (m2 - m1 < n1 - n2)):
                            bresenhamNegG1(m1, n1, m2, n2, xRes, yRes)

                        h += 1
                        if (h < len(toRender)):
                            x1 = int(toRender[h] * xRes * 1.0/2.0)
                            y1 = int(toRender[h + 1] * yRes * 1.0/2.0)

                    else:
                        x2 = int(toRender[h] * xRes * 1.0/2.0)
                        y2 = int(toRender[h+1] * yRes * 1.0/2.0)
                        
                        a1 = x1
                        b1 = y1
                        a2 = x2
                        b2 = y2

                        # Apply Bresenham's line algorithm
                        if (a2 <= a1):            
                            m1 = a2
                            n1 = b2
                            m2 = a1
                            n2 = b1
                        else:
                            m1 = a1
                            n1 = b1
                            m2 = a2
                            n2 = b2
                        # for the case where the positive slope <= 1 
                        if((n2 - n1 >= 0) and (m2 - m1 >= n2 - n1)):
                            bresenham(m1, n1, m2, n2, xRes, yRes)

                        # for the case where the positive slope > 1
                        elif((n2 - n1 >= 0) and (m2 - m1 < n2 - n1)):
                            bresenhamG1(m1, n1, m2, n2, xRes, yRes)

                        # for the case where the negative slope >= -1
                        elif((n2 - n1 < 0) and (m2 - m1 >= n1 - n2)):
                            bresenhamNeg(m1, n1, m2, n2, xRes, yRes)

                        # for the case where the negative slope < -1
                        elif((n2 - n1 < 0) and (m2 - m1 < n1 - n2)):
                            bresenhamNegG1(m1, n1, m2, n2, xRes, yRes)

                        h += 2
                        if (toRender[h] != -1):
                            x3 = int(toRender[h] * xRes * 1.0/2.0)
                            y3 = int(toRender[h+1] * yRes * 1.0/2.0)

                            a1 = a2
                            b1 = b2
                            a2 = x3
                            b2 = y3

                            # Apply Bresenham's line algorithm
                            if (a2 <= a1):            
                                m1 = a2
                                n1 = b2
                                m2 = a1
                                n2 = b1
                            else:
                                m1 = a1
                                n1 = b1
                                m2 = a2
                                n2 = b2
                            # for the case where the positive slope <= 1 
                            if((n2 - n1 >= 0) and (m2 - m1 >= n2 - n1)):
                                bresenham(m1, n1, m2, n2, xRes, yRes)

                            # for the case where the positive slope > 1
                            elif((n2 - n1 >= 0) and (m2 - m1 < n2 - n1)):
                                bresenhamG1(m1, n1, m2, n2, xRes, yRes)

                            # for the case where the negative slope >= -1
                            elif((n2 - n1 < 0) and (m2 - m1 >= n1 - n2)):
                                bresenhamNeg(m1, n1, m2, n2, xRes, yRes)

                            # for the case where the negative slope < -1
                            elif((n2 - n1 < 0) and (m2 - m1 < n1 - n2)):
                                bresenhamNegG1(m1, n1, m2, n2, xRes, yRes)                
                first = fo.readline()
                firstparse = parameter.parseString(first)
                if (firstparse[0] == 'normalIndex'):
                    print "ta-da"
                    i = 0
                    while(i < len(firstparse)):
                        k = firstparse[i]
                        # if the element is a comma, bracket, or coordIndex, then move on to next element
                        while ((k == ',') or (k == '[') or (k == ']') or (k == 'normalIndex')):
                            if (i < len(firstparse) - 1):
                                i += 1
                                k = firstparse[i]
                            else:
                                first = fo.readline()
                                firstparse = parameter.parseString(first)
                                i = 0
                                k = firstparse[i]

                        # put the 1st point in x1, y1
                        # multiply by 1.0/2.0 because the origin is in the center of the window
                        x1 = k
                        y1 = k

                        i += 1
                        #print "for normalindex: ", firstparse
                            
                first = fo.readline()
                firstparse = parameter.parseString(first)
        first = fo.readline()
    first = fo.readline()

for l in range(xRes*yRes):
    if(pixel[l] == 1):
        ppm.write(str(255) + " " + str(255) + " " + str(255) + "\n")
    else:
        ppm.write(str(0) + " " + str(0) + " " + str(0) + "\n")

ppm.close()
