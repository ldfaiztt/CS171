#!/usr/bin/python

from OpenGL.GL import *
from OpenGL.GL.shaders import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import pyparsing as pp
from math import pi, sin, cos, acos, sqrt
import numpy as np

def idle():
    
    # use catmull-rom
    # for some frame number, let's say frame 33, use frame 30, frame 45, frame 60 and frame 0
    # like wise, if say frame 56, use frame 45, frame 60, frame 0, and frame 30
    # the deltas will always be 15 since the difference between frames is 15

    # to pause or not to pause, that is the question (or key hehe lame alert)
    if (pause == 0):
        drawfunc()
    
def drawfunc():

    mvm = glGetFloatv(GL_MODELVIEW_MATRIX)

    global counterframe

    counterframe += 1
    frameIdx = counterframe % 75

    index = 0
    frameBlock = framenum[index]

    # while the index is less than the number of frames in the sample script
    # and also with the condition that the frame block number is greater than 
    # the frame index that we want
    while index < len(framenum) and frameBlock < frameIdx:
        frameBlock = framenum[index]
        index += 1
        
    # unfortunately, the above gives an index that is 1 too much in the case of 1-45
    if (frameIdx > 0 and index != len(framenum)):
        index -= 1

    # unfortunately again, the above above gives an index that is 1 too much in the case of
    # 46-60
    elif (frameIdx > framenum[len(framenum) - 2] and frameIdx <= framenum[len(framenum) - 1]):
        index -= 1

    if (frameIdx % 15 > 0):
        index -= 1

    print "the index of the frame ", frameIdx, "is in the the frameBlock ", framenum[index - 1]

    u = (frameIdx % 15)/15.0

    # This is for the translations, we use catmull-rom spline interpolation

    prevTranslation = np.array(translationsFram[index - 1])
    currTranslation = np.array(translationsFram[index % len(framenum)])
    nextTranslation = np.array(translationsFram[(index + 1) % len(framenum)])
    nextnextTranslation = np.array(translationsFram[(index + 2) % len(framenum)])

    print "the prevTranslation is: ", prevTranslation
    print "the currTranslation is: ", currTranslation
    print "the nextTranslation is: ", nextTranslation
    print "the nextnextTranslation is: ", nextnextTranslation

    kprime0Translate = 0.5*(currTranslation - prevTranslation)/15.0 + 0.5*(nextTranslation - currTranslation)/15.0
    kprime1Translate = 0.5*(nextTranslation - currTranslation)/15.0 + 0.5*(nextnextTranslation - nextTranslation)/15.0

    frameUTranslate = currTranslation * (2 * u * u * u - 3 * u * u + 1) + \
                      nextTranslation * (3 * u * u - 2 * u * u * u) + \
                      kprime0Translate * (u * u * u - 2 * u * u + u) + \
                      kprime1Translate * (u * u * u - u * u)

    # This is for the scale factors, we use catmull-rom spline interpolation

    prevScaleFactor = np.array(scalesFram[index - 1])
    currScaleFactor = np.array(scalesFram[index % len(framenum)])
    nextScaleFactor = np.array(scalesFram[(index + 1) % len(framenum)])
    nextnextScaleFactor = np.array(scalesFram[(index + 2) % len(framenum)])

    kprime0Scale = 0.5*(currScaleFactor - prevScaleFactor)/15.0 + 0.5*(nextScaleFactor - currScaleFactor)/15.0
    kprime1Scale = 0.5*(nextScaleFactor - currScaleFactor)/15.0 + 0.5*(nextnextScaleFactor - nextScaleFactor)/15.0

    frameUScale = currScaleFactor * (2 * u * u * u - 3 * u * u + 1) + \
                  nextScaleFactor * (3 * u * u - 2 * u * u * u) + \
                  kprime0Scale * (u * u * u - 2 * u * u + u) + \
                  kprime1Scale * (u * u * u - u * u)

    # This is for the rotations

    # previous frame, rotation, convert to quaternion
    preprevRotate = rotationsFram[index - 1]
    preprevX = preprevRotate[0]/(sqrt(preprevRotate[0]**2 + preprevRotate[1]**2 + preprevRotate[2]**2))
    preprevY = preprevRotate[1]/(sqrt(preprevRotate[0]**2 + preprevRotate[1]**2 + preprevRotate[2]**2))
    preprevZ = preprevRotate[2]/(sqrt(preprevRotate[0]**2 + preprevRotate[1]**2 + preprevRotate[2]**2))
    preprevAngle = preprevRotate[3] * pi/(2.0 * 180.0)

    #print "the previous frame rotate axis is: ", preprevX, ", ", preprevY, ", ", preprevZ
    #print "the previous angle is: ", preprevAngle

    prevqx = preprevX * sin(preprevAngle)
    prevqy = preprevY * sin(preprevAngle)
    prevqz = preprevZ * sin(preprevAngle)
    prevqw = cos(preprevAngle)

    prevnormalizing = sqrt(prevqx**2 + prevqy**2 + prevqz**2 + prevqw**2)

    prevQuaternion = np.array([prevqx/prevnormalizing, prevqy/prevnormalizing, 
                               prevqz/prevnormalizing, prevqw/prevnormalizing])

    # current frame, rotation, convert to quaternion
    precurrRotate = rotationsFram[index % len(framenum)]
    precurrX = precurrRotate[0]/(sqrt(precurrRotate[0]**2 + precurrRotate[1]**2 + precurrRotate[2]**2))
    precurrY = precurrRotate[1]/(sqrt(precurrRotate[0]**2 + precurrRotate[1]**2 + precurrRotate[2]**2))
    precurrZ = precurrRotate[2]/(sqrt(precurrRotate[0]**2 + precurrRotate[1]**2 + precurrRotate[2]**2))
    precurrAngle = precurrRotate[3] * pi/(2.0*180.0)

    #print "the current frame rotate axis is: ", precurrX, ", ", precurrY, ", ", precurrZ
    #print "the current angle is: ", precurrAngle

    currqx = precurrX * sin(precurrAngle)
    currqy = precurrY * sin(precurrAngle)
    currqz = precurrZ * sin(precurrAngle)
    currqw = cos(precurrAngle)

    currnormalizing = sqrt(currqx**2 + currqy**2 + currqz**2 + currqw**2)

    currQuaternion = np.array([currqx/currnormalizing, currqy/currnormalizing, 
                               currqz/currnormalizing, currqw/currnormalizing])

    #print "the current quaternion is: ", currQuaternion

    # next frame, rotation, convert to quaternion
    prenextRotate = rotationsFram[(index + 1) % len(framenum)]
    prenextX = prenextRotate[0]/(sqrt(prenextRotate[0]**2 + prenextRotate[1]**2 + prenextRotate[2]**2))
    prenextY = prenextRotate[1]/(sqrt(prenextRotate[0]**2 + prenextRotate[1]**2 + prenextRotate[2]**2))
    prenextZ = prenextRotate[2]/(sqrt(prenextRotate[0]**2 + prenextRotate[1]**2 + prenextRotate[2]**2))
    prenextAngle = prenextRotate[3] * pi/(2.0*180.0)

    nextqx = prenextX * sin(prenextAngle)
    nextqy = prenextY * sin(prenextAngle)
    nextqz = prenextZ * sin(prenextAngle)
    nextqw = cos(prenextAngle)

    nextnormalizing = sqrt(nextqx**2 + nextqy**2 + nextqz**2 + nextqw**2)

    nextQuaternion = np.array([nextqx/nextnormalizing, nextqy/nextnormalizing, 
                               nextqz/nextnormalizing, nextqw/nextnormalizing])

    # next next frame, rotation, convert to quaternion    

    prenextnextRotate = rotationsFram[(index + 2) % len(framenum)]
    prenextnextX = prenextnextRotate[0]/(sqrt(prenextnextRotate[0]**2 + prenextnextRotate[1]**2 + prenextnextRotate[2]**2))
    prenextnextY = prenextnextRotate[1]/(sqrt(prenextnextRotate[0]**2 + prenextnextRotate[1]**2 + prenextnextRotate[2]**2))
    prenextnextZ = prenextnextRotate[2]/(sqrt(prenextnextRotate[0]**2 + prenextnextRotate[1]**2 + prenextnextRotate[2]**2))
    prenextnextAngle = prenextnextRotate[3] * pi/(2.0*180.0)

    nextnextqx = prenextnextX * sin(prenextnextAngle)
    nextnextqy = prenextnextY * sin(prenextnextAngle)
    nextnextqz = prenextnextZ * sin(prenextnextAngle)
    nextnextqw = cos(prenextAngle)

    nextnextnormalizing = sqrt(nextnextqx**2 + nextnextqy**2 + nextnextqz**2 + nextnextqw**2)

    nextnextQuaternion = np.array([nextnextqx/nextnextnormalizing, nextnextqy/nextnextnormalizing, 
                                   nextnextqz/nextnextnormalizing, nextnextqw/nextnextnormalizing])

    # This is for the quaternions, we use catmull-rom spline interpolation

    kprime0Rotate = 0.5*(currQuaternion - prevQuaternion)/15.0 + 0.5*(nextQuaternion - currQuaternion)/15.0
    kprime1Rotate = 0.5*(nextQuaternion - currQuaternion)/15.0 + 0.5*(nextnextQuaternion - nextQuaternion)/15.0

    #print "the u-value is: ", u

    frameURotate = currQuaternion * (2 * u * u * u - 3 * u * u + 1) + \
                   nextQuaternion * (3 * u * u - 2 * u * u * u) + \
                   kprime0Rotate * (u * u * u - 2 * u * u + u) + \
                   kprime1Rotate * (u * u * u - u * u)

    #print "the inverse cosine of: ", frameURotate[3]

    # to make sure that the ratio is less than or equal to 1, to be able to do inverse cosine
    if (frameURotate[3] <= 1.0 and frameURotate[3] >= -1.0):
        rotateAngle = 2.0*acos(frameURotate[3])
    elif (frameURotate[3] < -1.0):
        rotateAngle = 2.0 * pi
    elif (frameURotate[3] > 1.0):
        rotateAngle = 2.0*0.0

    #print "the axes before dividing by sine are: ", frameURotate[0], ", ", frameURotate[1], ", ", frameURotate[2], ")"

    # to make sure the sine of the angle is greater than 0
    if (sin(rotateAngle) != 0):
        rotateX = frameURotate[0]/sin(rotateAngle)
        #print "the y-axis is: ", frameURotate[1]
        #print "the angle is: ", rotateAngle
        rotateY = frameURotate[1]/sin(rotateAngle)
        rotateZ = frameURotate[2]/sin(rotateAngle)
    else:
        rotateX = frameURotate[0]
        rotateY = frameURotate[1]
        rotateZ = frameURotate[2]

    rotateAngle = rotateAngle * 180.0/pi

    #print "the rotate angle is: ", rotateAngle
    #print "the rotate axis is: (", rotateX, ", ", rotateY, ", ", rotateZ, ")"

    print "the translate array is: ", frameUTranslate
    print "scale factor array is: ", frameUScale
    print "the rotate array is: ", rotateX, ", ", rotateY, ", ", rotateZ, ", ", rotateAngle

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(frameUTranslate[0], frameUTranslate[1], frameUTranslate[2])
    glRotatef(rotateAngle, rotateX, rotateY, rotateZ)
    glScalef(frameUScale[0], frameUScale[1], frameUScale[2])

    #glMultMatrixf(mvm)

    glutPostRedisplay()


# GLUT calls this function when a key is pressed. Here we just quit when ESC or
# 'q' is pressed.
def keyfunc(key, x, y):
    global pause
    global counterframe
    # To exit the program
    if key == 27 or key == 'q' or key == 'Q':
        exit(0)
    # To stop (pause) the program
    if key == 'S' or key == 's':
        pause = 1
    # To play (start) the program
    if key == 'P' or key == 'p':
        pause = 0
    # To forward one frame
    if key == 'F' or key == 'f':
        pause = 1
        drawfunc()
    # suppose to decrement the time by 1
    if key == 'R' or key == 'r':
        pause = 1
        counterframe -= 2
        drawfunc()

def display():

    glClearColor(0.0, 0.0, 0.0, 1.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #glLoadIdentity()    

    glPushMatrix()
    glColor3f(1.0, 1.0, 0.0)
    yellowcylinder = gluNewQuadric()
    # to make it far away
    glTranslatef(0.0, 0.0, -4.0)
    glRotatef(90.0,0.0,1.0,0.0)

    # gluQuadric object, base, top, height, slices, stacks
    gluCylinder(yellowcylinder, 0.01, 0.01, 0.1, 30, 50)

    glTranslatef(0.0, 0.0, 0.1)
    glColor3f(0.0, 1.0, 0.0)
    glRotatef(0.0,0.0,1.0,0.0)
    greencylinder = gluNewQuadric()
    
    gluCylinder(greencylinder, 0.01, 0.01, 0.1, 3, 5)

    glTranslatef(0.005, 0.01, 0.0)
    glColor3f(0.0, 0.0, 1.0)
    glRotatef(-90.0,1.0,0.0,0.0)
    redcylinder = gluNewQuadric()
    
    gluCylinder(redcylinder, 0.01, 0.01, 0.2, 3, 5)
    

    glTranslatef(0.0, 0.1, 0.201)
    glColor3f(1.0, 0.0, 1.0)
    pinkcylinder = gluNewQuadric()
    glRotatef(90.0, 1.0, 0.0, 0.0)

    gluCylinder(pinkcylinder, 0.01, 0.01, 0.1, 3, 5)

    glTranslatef(0.0, 0.0, 0.1)
    glColor3f(0.0, 1.0, 1.0)
    cyancylinder = gluNewQuadric()
    glRotatef(0.0, 1.0, 0.0, 0.0)

    gluCylinder(cyancylinder, 0.01, 0.01, 0.1, 3, 5)

    

    glPopMatrix()

    glutSwapBuffers()  
      

if __name__ == "__main__":

    glutInit(sys.argv)

    # x dimension size
    xRes = int(sys.argv[1])

    # y dimension size
    yRes = int(sys.argv[2])

    # iv file name to input
    samplescript = sys.argv[3]

    glutInitDisplayMode(GLUT_RGBA | GLUT_SINGLE | GLUT_DEPTH)

    glutInitWindowSize(xRes, yRes)
    glutInitWindowPosition(300, 100)

    glutCreateWindow("CS171 HW7")

    
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
    period = pp.Literal(".")
    sharp = pp.Literal("#")

    # Optional added for the additional number for rotation
    parameter = pp.Optional(sharp) + pp.Optional(pp.Word( pp.alphas )) + \
                pp.Optional(pp.Word( pp.alphas ) + period + pp.Word(pp.alphas)) + \
                pp.Optional(leftBracket) + pp.Optional(leftBrace) + \
                pp.Optional(rightBracket) + pp.Optional(rightBrace) + \
                pp.ZeroOrMore(number + pp.Optional(comma))

    # Open a file
    fo = open(samplescript, "r")

    first = fo.readline()

    # the total number of frames parsed here
    firstparse = parameter.parseString(first)

    totalframes = firstparse[0]

    first = fo.readline()

    # The frame numbers in the .script file
    framenum = []

    # The translations accumulated into a list
    translationsFram = []

    # The scale factors accumulated into a list
    scalesFram = []

    # The rotations accumulated into a list
    rotationsFram = []

    # count the number of frame
    global counterframe
    counterframe = -1

    # Pause, set to no pause
    global pause
    pause = 1

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    #glOrtho(-15.0, 15.0, -15.0, 15.0, 1.0, 30.0)
    glFrustum(-1, 1, -1, 1, 1.0, 30.0)

    #glFrustum(-.3, 0.3, -0.3, 0.3, 1.0, 30.0)

    #gluLookAt(0.0, 0.0, -5.0, 0.0, 0.0, 0.0, 

    # viewing angle is 88 degrees, distance between viewer and nearest clipping plane is 0
    # distance between viewer and furthest clipping plane is 10
    #gluPerspective(89.8, 1.0, 0.0, 30.0);

    #glOrtho(0.0, 20.0, 0.0, 20.0, -20.0, 20.0)

    while (first != ''):
        firstparse = parameter.parseString(first)

        # if we reach a Frame block, then store the translation, scale, and rotation, or whatever is available.
        if (firstparse[0] == "Frame"):

            # add the frame number associated with the Frame term
            framenum.append(firstparse[1])

            # now let's investigate this Frame block
            first = fo.readline()
            firstparse = parameter.parseString(first)

            # investigate this particular frame block until we reach the next frame block or the end of the file
            while (first != '' and firstparse[0] != "Frame"):
                if (firstparse[0] == "translation"):
                    translation = [firstparse[1], firstparse[2], firstparse[3]]
                    translationsFram.append(translation)
                
                elif (firstparse[0] == "scale"):
                    scale = [firstparse[1], firstparse[2], firstparse[3]]
                    scalesFram.append(scale)

                elif (firstparse[0] == "rotation"):
                    rotation = [firstparse[1], firstparse[2], firstparse[3], firstparse[4]]
                    rotationsFram.append(rotation)
                first = fo.readline()
                firstparse = parameter.parseString(first)

    print "the total amount of frames is: ", totalframes

    print "the frame numbers in the file are: ", framenum

    print "The translations for the frames are: ", translationsFram

    print "the scale factors for the frame are: ", scalesFram

    print "the rotations for the frame are: ", rotationsFram

    fo.close()

    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glutDisplayFunc(display) 

    glutIdleFunc(idle)

    glutKeyboardFunc(keyfunc)
    glutMainLoop()
