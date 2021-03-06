#!/usr/bin/python

import numpy as np
import pyparsing as pp
from math import*
from rotationerror import RotateError
import sys

# Get the file name and open it
fileParse = raw_input("Enter the file you want to parse: ")
print "The file name is : ", fileParse

# Read the file
fo = open(fileParse, "r")

# define grammar
# number is real
number = pp.Regex(r"-?\d+(\.\d*)?([Ee][+-]?\d+)?")
number.setParseAction(lambda toks:float(toks[0]))

# Optional added for the additional number for rotation
parameter = pp.Word(pp.alphas) + number + number + number + pp.Optional(number)

# first line of file: the options are either translation, rotation, or scale factor
first = fo.readline()

line1 = parameter.parseString(first)

print line1

if (line1[0] == "translation"):
    translateX = line1[1]
    translateY = line1[2]
    translateZ = line1[3]

elif (line1[0] == "rotation"):
    x = line1[1]
    y = line1[2]
    z = line1[3]
    angle = line1[4]

else:
    scaleFactorX = line1[1]
    scaleFactorY = line1[2]
    scaleFactorZ = line1[3]

# second line of file: the options are either translation, rotation, or scale factor
second = fo.readline()

line2 = parameter.parseString(second)

print line2

if (line2[0] == "translation"):
    translateX = line2[1]
    translateY = line2[2]
    translateZ = line2[3]

elif (line2[0] == "rotation"):
    x = line2[1]
    y = line2[2]
    z = line2[3]
    angle = line2[4]

else:
    scaleFactorX = line2[1]
    scaleFactorY = line2[2]
    scaleFactorZ = line2[3]

# third line of file: the options are either translation, rotation, or scale factor
third = fo.readline()

line3 = parameter.parseString(third)

print line3

if (line3[0] == "translation"):
    translateX = line3[1]
    translateY = line3[2]
    translateZ = line3[3]

elif (line3[0] == "rotation"):
    prelimX = line[1]
    prelimY = line[2]
    prelimZ = line[3]
    x = prelimX/sqrt(prelimX**2 + prelimY**2 + prelimZ**2)
    y = prelimY/sqrt(prelimX**2 + prelimY**2 + prelimZ**2)
    z = prelimZ/sqrt(prelimX**2 + prelimY**2 + prelimZ**2)
    angle = line3[4]

else:
    scaleFactorX = line3[1]
    scaleFactorY = line3[2]
    scaleFactorZ = line3[3]

if ((x == 0) and (y == 0) and (z == 0)):
    raise RotateError


translateMat = np.array([[1, 0, 0, translateX], 
                         [0, 1, 0, translateY], 
                         [0, 0, 1, translateZ], 
                         [0, 0, 0, 1]])

scaleFactorMat = np.array([[scaleFactorX, 0, 0, 0], 
                           [0, scaleFactorY, 0, 0], 
                           [0, 0, scaleFactorZ, 0], 
                           [0, 0, 0, 1]])

rotationMat = np.array([[x**2 + (1 - x**2)*cos(angle), x*y*(1-cos(angle)) - z*sin(angle), x*z*(1-cos(angle)) + y*sin(angle), 0],
		                [x*y*(1-cos(angle)) + z*sin(angle), y**2 + (1-y**2)*cos(angle), y*z*(1-cos(angle)) - x*sin(angle), 0],
		                [x*z*(1-cos(angle)) - y*sin(angle), y*z*(1-cos(angle)) + x*sin(angle), z**2 + (1-z**2)*cos(angle), 0],
		                [0, 0, 0, 1]])

# the 6 possible orders of translation, rotation, and scaleFactor (to multiple matrices)
if ((line1[0] == "translation") and (line2[0] == "rotation") and (line3[0] == "scaleFactor")):
    mat1 = np.dot(translateMat, rotationMat)
    mat2 = np.dot(mat1, scaleFactorMat)

elif ((line1[0] == "translation") and (line2[0] == "scaleFactor") and (line3[0] == "rotation")):
    mat1 = np.dot(translateMat, scaleFactorMat)
    mat2 = np.dot(mat1, rotation)

elif ((line1[0] == "rotation") and (line2[0] == "translation") and (line3[0] == "scaleFactor")):
    mat1 = np.dot(rotationMat, translateMat)
    mat2 = np.dot(mat1, scaleFactorMat)

elif ((line1[0] == "rotation") and (line2[0] == "scaleFactor") and (line3[0] == "translation")):
    mat1 = np.dot(rotationMat, scaleFactorMat)
    mat2 = np.dot(mat1, translateMat)

elif ((line1[0] == "scaleFactor") and (line2[0] == "rotation") and (line3[0] == "translation")):
    mat1 = np.dot(scaleFactorMat, rotationMat)
    mat2 = np.dot(mat1, translateMat)

else:
    mat1 = np.dot(scaleFactorMat, translateMat)
    mat2 = np.dot(mat1, rotationMat)

print mat2

fo.close()

