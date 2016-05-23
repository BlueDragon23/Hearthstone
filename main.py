"""
Hearthstone Computer Graphics
@author: Aidan Goldthorpe

----------------------
Graphical display of Hearthstone card statistics

ESC: exit
"""

import json
import colorsys
from math import *
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

#####################################################################


CamPhi = 30
CamTheta = 60
CamRange = 250
PerspectiveAngle = 45
MaximumDataPoint = 0


# Initialise GLUT and a few other things
# create and return a window
def InitGLUT(nWidth, nHeight, title=""):
    glutInit(title)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(nWidth, nHeight)
    glutInitWindowPosition(0, 0)


#
# A general OpenGL initialisation function that sets various initial parameters.
# We call this right after out OpenGL window is created.
#
def InitGL(nWidth, nHeight):
    # use black when clearing the colour buffers -- this will give us a black
    # background for the window
    glClearColor(0.0, 0.0, 0.0, 0.0)
    # enable the depth buffer to be cleared
    glClearDepth(1.0)
    # set which type of depth test to use
    glDepthFunc(GL_LESS)
    # enable depth testing
    glEnable(GL_DEPTH_TEST)
    # enable smooth colour shading
    glShadeModel(GL_SMOOTH)

    ResizeGLScene(nWidth, nHeight)


#
# The function called when our window is resized. This won't happen if we run
# in full screen mode.
#
def ResizeGLScene(nWidth, nHeight):
    # prevent a divide-by-zero error if the window is too small
    if nHeight == 0:
        nHeight = 1

    # reset the current viewport and recalculate the perspective transformation
    # for the projection matrix
    glViewport(0, 0, nWidth, nHeight)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(PerspectiveAngle, float(nWidth) / float(nHeight), 0.1, 1000.0)
    # glOrtho(-w,w,-h,h,1,20000)
    glMatrixMode(GL_MODELVIEW)
    # glLoadIdentity()


def readData() -> []:
    global MaximumDataPoint
    file = open("C:\\Users\\Aidan\\Dropbox\\University\\COSC3000\ComputerGraphics\\cards.collectible.json")

    cards = json.load(file)

    mana = []
    health = []
    attack = []
    for card in cards:
        if card['type'] != 'MINION':
            continue
        mana.append(card['cost'])
        health.append(card['health'])
        attack.append(card['attack'])

    values = [(mana[i], health[i], attack[i]) for i in range(len(mana))]
    MaximumDataPoint = max([max(x[i] for x in values) for i in range(3)]) * 10
    return values


def getDrawable(values: []) -> []:
    unique = set(values)
    counts = {x: values.count(x) for x in values}
    return [(counts[val], val[0], val[1], val[2]) for val in unique]

def handler(button, state, x: int, y: int):
    if state != GLUT_DOWN:
        return
    print("x = {}, y = {}".format(x, y))
    # getColor
    # color = scale*x/maxX + minVal
    # x = (color - minVal)*maxX/scale
    window_height = glutGet(GLUT_WINDOW_HEIGHT)
    pixel = glReadPixels(x, window_height - y - 1, 1, 1, GL_RGB, GL_FLOAT)
    # Access the first and only list of colours
    pixel = pixel[0][0]
    # Select object based on colour
    print(pixel)
    coords = [round(x, -1)//10 for x in getCoordsFromColour(pixel)]
    print(coords)
    return None


#####################################################################

def drawVertices(x):
    for i in range(len(x)):
        glVertex3fv(x[i])


def drawAxes(h):
    # h : length of the axes
    # draw axis X in red
    # draw axis Y in green
    # draw axis Z in blue

    x = [h, 0, 0]
    y = [0, h, 0]
    z = [0, 0, h]
    o = [0, 0, 0]

    glBegin(GL_LINES)

    glColor3fv([1, 0, 0])
    glVertex3fv(o)
    glVertex3fv(x)

    glColor3fv([0, 1, 0])
    glVertex3fv(o)
    glVertex3fv(y)

    glColor3fv([0, 0, 1])
    glVertex3fv(o)
    glVertex3fv(z)

    glEnd()

def getColour(val):
    minVal = 0.2
    scale = 0.8
    return 1 - (scale * val / MaximumDataPoint + minVal)


def getCoordsFromColour(pixel):
    minVal = 0.2
    scale = 0.8
    [x, y, z] = [(- (col - 1) - minVal)*MaximumDataPoint/scale for col in pixel]
    return [x, y, z]


def drawSphere(radius: int, x: int, y: int, z: int) -> None:
    # Modify in isolation
    glPushMatrix()

    glTranslate(x, y, z)
    glColor4f(1, 1, 1, 1)
    #glEnable(GL_LIGHT0)
    #glEnable(GL_LIGHTING)
    xColour = getColour(x)
    yColour = getColour(y)
    zColour = getColour(z)
    glColor3fv([xColour, yColour, zColour])
    # glMaterialfv(GL_FRONT, GL_DIFFUSE, [1*x/100, 1*y/100, 1*z/100, 1])
    # Sphere model
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluQuadricTexture(quadric, GL_TRUE)
    gluSphere(quadric, radius, 32, 32)

    #glDisable(GL_LIGHTING)

    glPopMatrix()


#####################################################################

def drawCube(size):
    a = [size, size, -size]
    b = [-size, size, -size]
    c = [-size, size, size]
    d = [size, size, size]
    e = [-size, -size, size]
    f = [-size, -size, -size]
    g = [size, -size, size]
    h = [size, -size, -size]

    glBegin(GL_QUADS)

    drawVertices([a, b, c, d])
    drawVertices([b, f, e, c])
    drawVertices([c, d, g, e])
    drawVertices([d, g, h, a])
    drawVertices([e, f, h, g])
    drawVertices([f, b, a, h])

    glEnd()


#####################################################################

def DrawGLScene():
    # clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # reset the matrix stack with the identity matrix
    glLoadIdentity()

    spacing = 10
    # camera setup

    r_xz = CamRange * cos(CamPhi * pi / 180)
    x = r_xz * sin(CamTheta * pi / 180)
    y = CamRange * sin(CamPhi * pi / 180)
    z = r_xz * cos(CamTheta * pi / 180)

    gluLookAt(x, y, z,
              0.0, 0.0, 0.0,
              0.0, 0.0, 1.0)

    drawAxes(1500)
    # data is a 4-tuple containing (numElems, mana, health, attack)
    mostPopular = max([x[0] for x in data])
    for i in range(len(data)):
        drawSphere(data[i][0] * (spacing / 2) / mostPopular, data[i][1] * spacing, data[i][2] * spacing,
                   data[i][3] * spacing)

    # since this is double buffered, we need to swap the buffers in order to
    # display what we just drew
    glutSwapBuffers()

    # Added for graphics processors that do not employ frame-rate limiting
    time.sleep(0.01)


def KeyPressed(key, x, y):
    global show_axes, fill_polygons
    global CamPhi, CamTheta, CamRange

    # 'ord' gives the ascii int code of a character
    # 'chr' gives the character associated to the ascii int code.
    key = ord(key)

    if key == 27:  # Escape
        glutDestroyWindow(hWindow)
        sys.exit()
    elif key == ord('S') or key == ord('s'):
        CamPhi -= 1
        if CamPhi < -90:
            CamPhi = -90  # Limit
    elif key == ord('W') or key == ord('w'):
        CamPhi += 1
        if CamPhi > 90:
            CamPhi = 90  # Limit
    elif key == ord('A') or key == ord('a'):
        CamTheta -= 1
        if CamTheta < 0:
            CamTheta += 360  # Modulus
    elif key == ord('D') or key == ord('d'):
        CamTheta += 1
        if CamTheta > 360:
            CamTheta -= 360  # Modulus
    elif key == ord('E') or key == ord('e'):
        CamRange -= 1
    elif key == ord('Q') or key == ord('q'):
        CamRange += 1


if __name__ == "__main__":
    # Info about the OpenGL version
    # print "GPU                      = ",glGetString(GL_VENDOR)
    # print "Renderer                 = ",glGetString(GL_RENDERER)
    # print "OpenGL                   = ",glGetString(GL_VERSION)

    # Defining global variables
    global hWindow, nWidth, nHeight
    global show_axes, fill_polygons
    global data

    # screen size
    nWidth = 1080
    nHeight = 720

    # Initialise GLUT and a few other things
    InitGLUT(nWidth, nHeight)

    # create our window
    hWindow = glutCreateWindow(b"Hearthstone Cards")

    show_axes = True
    fill_polygons = True
    camera_rotation = 60

    # Read in our data
    data = readData()
    data = getDrawable(data)

    # setup the display function callback
    glutDisplayFunc(DrawGLScene)

    # setup the idle function callback -- if we idle, we just want to keep
    # drawing the screen
    glutIdleFunc(DrawGLScene)
    # setup the window resize callback -- this is only needed if we arent going
    # full-screen
    glutReshapeFunc(ResizeGLScene)

    # setup the keyboard function callback to handle key presses
    glutKeyboardFunc(KeyPressed)
    # setup the mouse callback
    glutMouseFunc(handler)

    # Tell people how to exit, then start the program...
    print("To quit: Select OpenGL display window with mouse, then press ESC key.")

    InitGL(nWidth, nHeight)

    # enter the window's main loop to set things rolling
    glutMainLoop()
