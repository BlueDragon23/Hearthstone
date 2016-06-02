import json
from math import *
import time
from OpenGL.GL import *
import logging
logging.basicConfig(level=logging.DEBUG)
OpenGL.FULL_LOGGING = True
OpenGL.ERROR_ON_COPY = True
from OpenGL.GLU import *
from OpenGL.GLUT import *
import data
import sys
from PIL import Image
from io import BytesIO
import numpy
from OpenGL.arrays import vbo
import random



# Globals
CamPhi = 30
CamTheta = 90
CamRange = -3000
PhiRate = 3
ThetaRate = 3
RangeRate = 20
PerspectiveAngle = 45
MaximumDataPoint = 0
cardback = []
vertexBuffers = 0
boardWidth = 3080
boardHeight = 1400
mana = 3
TimeRemaining = 0
CamStep = 0
PhiStep = 0
ThetaStep = 0
previousTime = 0
UpdateFunction = lambda : 1
Transitioning = False

# Textures
textureIds = []
BoardId = 0
BoardImage = None
hand = []
friendlyBoard = []
enemyBoard = []
potentialBoard1 = {"friendly" : [], "enemy" : []}
potentialBoard2 = {}
potentialBoard3 = {}
previousBoard = {}
textureDict = {} # Map card names to their textures



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
    global BoardImage
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

    # Load textures
    BoardImage = Image.open("cards/Board.png")

    InitTexturing()

    ResizeGLScene(nWidth, nHeight)


#
# Initialises the textures being used for the scene
#
def InitTexturing():
    global BoardId, BoardImage

    # create textures
    BoardId = glGenTextures(1)
    print(BoardImage, BoardId)
    # just use linear filtering
    glBindTexture(GL_TEXTURE_2D, BoardId)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    data = BytesIO()
    r, g, b, a = BoardImage.split()
    dup = Image.merge("RGB", (r, g, b))
    dup.save(data, format="BMP")
    glTexImage2D(GL_TEXTURE_2D, 0, 4,
                 dup.width, dup.height,
                 0, GL_BGR, GL_UNSIGNED_BYTE, data.getvalue())


def init_texture(origName: str):
    if origName in textureDict:
        return
    name = origName.lower()
    name = "-".join(name.split())
    name = str.replace(name, "'", "")
    image = Image.open("cards/{}.png".format(name))

    # create textures
    id = glGenTextures(1)
    textureIds.append(id)

    # just use linear filtering
    glBindTexture(GL_TEXTURE_2D, id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    data = BytesIO()
    r, g, b, a = image.split()
    dup = Image.merge("RGB", (r, g, b))
    dup.save(data, format="BMP")
    glTexImage2D(GL_TEXTURE_2D, 0, 4,
                 dup.width, dup.height,
                 0, GL_BGR, GL_UNSIGNED_BYTE, data.getvalue())
    textureDict[origName] = id


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
    gluPerspective(PerspectiveAngle, float(nWidth) / float(nHeight), 0.1, 10000.0)
    glMatrixMode(GL_MODELVIEW)

def handler(button, state, x: int, y: int):
    if state != GLUT_DOWN:
        return
    window_width = glutGet(GLUT_WINDOW_WIDTH)
    window_height = glutGet(GLUT_WINDOW_HEIGHT)
    # The following values are based on how the overlay is constructed
    # If that changes, this will break
    size = 50
    pixel = glReadPixels(x, window_height - y, 1, 1, GL_RGB, GL_FLOAT)[0][0]
    if x < size and y < size:
        KeyPressed('1', x, y)
    elif window_width/2 - size/2 < x < window_width/2 + size/2 \
        and y < size:
        KeyPressed('2', x, y)
    elif x > window_width - size and y < size:
        KeyPressed('3', x, y)
    elif 0.105 < pixel[0] < 0.115:
        # Decrease
        modify_value(x, window_width, lambda a, b: a - b)
    elif 0.115 < pixel[0] < 0.125:
        modify_value(x, window_width, lambda a, b: a + b)
    elif 0.095 < pixel[0] < 0.105:
        set_value(x, window_width)


def modify_value(x, window_width, op):
    global ThetaRate, RangeRate, PhiRate
    if x < window_width/3:
        ThetaRate = min(max(op(ThetaRate, 1), 1), 50)
        print(ThetaRate)
    elif x > 2*window_width/3:
        RangeRate = min(max(op(RangeRate, 1), 1), 50)
    else:
        PhiRate = min(max(op(PhiRate, 1), 1), 50)

def set_value(x, window_width):
    global ThetaRate, PhiRate, RangeRate
    padding = 50
    if x < window_width/3:
        ThetaRate = 50 * ((x - padding)/(window_width/3 - 2*padding))
    elif x > 2*window_width/3:
        x = x - 2*window_width/3
        RangeRate = 50 * ((x - padding)/(window_width/3 - 2*padding))
    else:
        x = x - window_width/3
        PhiRate = 50 * ((x - padding)/(window_width/3 - 2*padding))

###################################################################################

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

def draw_board():
    """
    :param x0:
    :param y0:
    :param z0:
    :param x1:
    :param y1:
    :param z1:
    :param isVertical: Orientation should be true for vertical, false for flat
    :return:
    """
    glPushMatrix()
    glBindTexture(GL_TEXTURE_2D, BoardId)
    width = boardWidth
    height = boardHeight
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-width/2, -height/2, 0)
    glTexCoord2f(1, 0)
    glVertex3f(width/2, -height/2, 0)
    glTexCoord2f(1, 1)
    glVertex3f(width/2, height/2, 0)
    glTexCoord2f(0, 1)
    glVertex3f(-width/2, height/2, 0)
    glEnd()
    glPopMatrix()

def draw_minions(minions):
    numCards = len(minions)
    for i, minion in enumerate(minions):
        glPushMatrix()
        glBindTexture(GL_TEXTURE_2D, textureDict[minion['name']])
        position = ((numCards) * ( -150 ) + 300 * i , -500, 0)
        glTranslatef(position[0], position[1], position[2])
        draw_card()
        draw_cardback()
        if minion['type'] == 'MINION':
            draw_status_bars(minion)
        glPopMatrix()


def draw_card():
    glDisable(GL_LIGHTING)
    height = 400
    width = 275
    glColor3f(1,1,1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(0, 0, 0)
    glTexCoord2f(1, 0)
    glVertex3f(width, 0, 0)
    glTexCoord2f(1, 1)
    glVertex3f(width, height, 0)
    glTexCoord2f(0, 1)
    glVertex3f(0, height, 0)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_status_bars(minion):
    width = 25
    scaling = 25
    attack = int(minion['attack'])
    health = int(minion['health'])

    def draw_rect(height):
        glRectf(0, 0, width, height)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    # Draw attack
    glPushMatrix()
    glColor3fv([1, 1, 0])
    glTranslatef(50, 70, 0)
    glRotatef(90, 1, 0, 0)
    draw_rect(attack*scaling)
    glTranslatef( width, 0, 0 )
    glRotatef( 90, 0, 1, 0 )
    draw_rect(attack*scaling)
    glTranslatef( width, 0, 0 )
    glRotatef( 90, 0, 1, 0 )
    draw_rect(attack*scaling)
    glTranslatef( width, 0, 0 )
    glRotatef( 90, 0, 1, 0 )
    draw_rect(attack*scaling)
    glTranslatef( 0, attack*scaling, -width)
    glRotatef(90, 1, 0, 0)
    glRectf(0, 0, width, width)
    glPopMatrix()

    # Draw health
    glPushMatrix()

    glColor3fv([1, 0, 0])
    glTranslatef(300 - 50, 70, 0)
    glRotatef(90, 1, 0, 0)
    draw_rect(health*scaling)
    glTranslatef( width, 0, 0 )
    glRotatef( 90, 0, 1, 0 )
    draw_rect(health*scaling)
    glTranslatef( width, 0, 0 )
    glRotatef( 90, 0, 1, 0 )
    draw_rect(health*scaling)
    glTranslatef( width, 0, 0 )
    glRotatef( 90, 0, 1, 0 )
    draw_rect(health*scaling)
    glTranslatef( 0, health*scaling, -width)
    glRotatef(90, 1, 0, 0)
    glRectf(0, 0, width, width)
    glPopMatrix()
    glColor3fv([1, 1, 1])
    glEnable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)

def draw_cardback():
    glDisable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslate(275/2, 400/2, -10)
    glScale(6.66, 6.875, 1)
    glRotate(90, 0, 1, 0)
    for i in range(len(cardback)):
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        cardbackNormals[i].bind()
        glNormalPointer(GL_FLOAT, 0, cardbackNormals[i])
        cardbackVertices[i].bind()
        material = data.find_mtl(cardback[i]["material"], materials)
        # print(material)
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.1, 0.1, 0.1])
        # glMaterialfv(GL_FRONT, GL_SPECULAR, material["specular"])
        # glMaterialfv(GL_FRONT, GL_SHININESS, [2])
        # glMaterialfv(GL_FRONT, GL_AMBIENT, material["ambient"])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, material["diffuse"])

        glVertexPointer(3, GL_FLOAT, 0, cardbackVertices[i])
        glDrawArrays(GL_TRIANGLES, 0, len(cardbackVertices[i]))
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
    glPopMatrix()
    glEnable(GL_TEXTURE_2D)

def draw_decks():
    glPushMatrix()
    glTranslate(boardWidth/2 - 500, 0, -250)
    glRotate(90, 0, 0, 1)
    glRotate(90, 1, 0, 0)
    difference = 20
    for _ in range(5):
        draw_cardback()
        glTranslate(0, 0, difference)
    glTranslate(-boardHeight/4, 0, -difference*5)
    for _ in range(5):
        draw_cardback()
        glTranslate(0, 0, difference)
    glPopMatrix()

def draw_mana():
    glDisable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslate(boardWidth/5, -boardHeight/2, -5)
    radius = 30
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [41/255, 85/255, 146/255])
    glEnable(GL_NORMALIZE)
    for _ in range(mana):
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, 10)
        glNormal3f(-0.33, 0, 1)
        glVertex3f(-radius, 0, 0)
        glNormal3f(-0.25, 0.25, 1)
        glVertex3f(-radius/2, radius, 0)
        glNormal3f(0.25, 0.25, 1)
        glVertex3f(radius/2, radius, 0)
        glNormal3f(0.33, 0, 1)
        glVertex3f(radius, 0, 0)
        glNormal3f(0.25, -0.25, 1)
        glVertex3f(radius/2, -radius, 0)
        glNormal3f(-0.25, -0.25, 1)
        glVertex3f(-radius/2, -radius, 0)
        glNormal3f(-0.33, 0, 1)
        glVertex3f(-radius, 0, 0)
        glEnd()
        glTranslate(radius*2, 0, 0)
    glDisable(GL_NORMALIZE)
    glPopMatrix()
    glEnable(GL_TEXTURE_2D)

def draw_game(friendlyMinions, enemyMinions):
    glPushMatrix()
    draw_minions(friendlyMinions)
    glPushMatrix()
    glTranslate(0, 500, 0)
    draw_minions(enemyMinions)
    glPopMatrix()
    draw_decks()
    draw_mana()
    glTranslate(0, -100, -20)
    draw_board()
    glPopMatrix()

def draw_numbers(width, height):
    def draw_square(x, y, size):
        """
        Treats the top left corner as 0, 0
        """
        glColor([0.8 * x for x in [1, 1, 1]])
        glBegin(GL_QUADS)
        glVertex2f(x, height - y)
        glVertex2f(x, height - y - size)
        glVertex2f(x + size, height - y - size)
        glVertex2f(x + size, height - y)
        glEnd()

    size = 50
    margin = 10
    draw_square(0, 0, size)
    glColor(0, 0, 0)
    glBegin(GL_LINE_STRIP)
    glVertex2f(size / 2, height - margin)
    glVertex2f(size / 2, height - (size - margin))
    glEnd()
    draw_square(width / 2 - size / 2, 0, size)
    glColor(0, 0, 0)
    glBegin(GL_LINE_STRIP)
    glVertex2f(width / 2 - size / 2 + margin, height - margin)
    glVertex2f(width / 2 + size / 2 - margin, height - margin)  # -
    glVertex2f(width / 2 + size / 2 - margin, height - size / 2)  # |
    glVertex2f(width / 2 - size / 2 + margin, height - size / 2)  # -
    glVertex2f(width / 2 - size / 2 + margin, height - size + margin)  # |
    glVertex2f(width / 2 + size / 2 - margin, height - size + margin)  # -
    glEnd()
    draw_square(width - size, 0, size)
    glColor(0, 0, 0)
    glBegin(GL_LINE_STRIP)
    glVertex2f(width - size + margin, height - margin)
    glVertex2f(width - margin, height - margin)  # -
    glVertex2f(width - margin, height - size / 2)  # |
    glVertex2f(width - size + margin, height - size / 2)  # -
    glVertex2f(width - margin, height - size / 2)  # -
    glVertex2f(width - margin, height - size + margin)  # |
    glVertex2f(width - (size - margin), height - size + margin)  # -
    glEnd()

def draw_overlay():
    """
    Draws a 2D overlay on top of the screen, as a HUD allowing some user interaction

    Warning: If this function is changed, the handler may need
    to be modified
    :return:
    """
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    gluOrtho2D(0, width, 0, height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    draw_numbers(width, height)
    # Bottom Panel
    glColor(0.8, 0.8, 0.8)
    glRectf(0, 0, width, height/8)
    # Sliders
    padding = width / 20
    def draw_slider(x):
        glBegin(GL_TRIANGLES)
        glColor(0.11, 0.11, 0.11)
        glVertex2f(x + padding/3, height/10/2)
        glVertex2f(x + 2*padding/3, 2*height/10/3)
        glVertex2f(x + 2*padding/3, height/10/3)
        glColor(0.12, 0.12, 0.12)
        glVertex2f(x + width/3 - padding/3, height/10/2)
        glVertex2f(x + width/3 - 2*padding/3, 2*height/10/3)
        glVertex2f(x + width/3 - 2*padding/3, height/10/3)
        glEnd()
        glColor(0.1, 0.1, 0.1)
        glRectf(x + padding, padding, x + width/3 - padding, height/10 - padding)
    draw_slider(0)
    draw_slider(width/3)
    draw_slider(2*width/3)
    # Slider position
    glColor(0.5, 0.5, 0.5)
    vars = []
    vars.extend([ThetaRate, PhiRate, RangeRate])
    for i in range(3):
        x = i*width/3 + padding + vars[i]/50*(width/3 - padding*2)
        glRectf(x - 5, padding, x + 5, height/10 - padding)
    # Text
    labels = ["Horizontal Pan", "Vertical Pan", "Zoom Rate"]
    for i in range(3):
        glRasterPos2f(i*width/3 + padding, height/10-10)
        text = labels[i]
        for c in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    glPopMatrix()

def DrawGLScene():
    global CamRange, CamPhi, CamTheta, TimeRemaining, previousTime, CamStep, ThetaStep, PhiStep, Transitioning
    glEnable(GL_DEPTH_TEST)
    # clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    ResizeGLScene(width, height)
    glMatrixMode(GL_MODELVIEW)
    # reset the matrix stack with the identity matrix
    glLoadIdentity()

    # camera setup
    # r_xz = CamRange * cos(CamPhi * pi / 180)
    # x = r_xz * sin(CamTheta * pi / 180)
    # y = CamRange * sin(CamPhi * pi / 180)
    # z = r_xz * cos(CamTheta * pi / 180)
    #
    # gluLookAt(x, y, z,
    #           0.0, 0.0, 0.0,
    #           0.0, 0.0, 1.0)
    if (TimeRemaining >= 0):
        CamRange += CamStep
        CamPhi += PhiStep
        CamTheta += ThetaStep
        TimeRemaining -= 100
        if TimeRemaining <= 0 and Transitioning:
            UpdateFunction()
            CamPhi = 0
            CamTheta = 90
            CamRange = -800
            # Reset to normal view
            TimeRemaining = 2000
            CamStep = (-2000 - CamRange) / (TimeRemaining / 100)
            PhiStep = (30 - CamPhi) / (TimeRemaining / 100)
            ThetaStep = (90 - CamTheta) / (TimeRemaining / 100)
            Transitioning = False
    print("Theta: {}, Phi: {}, Range: {}".format(CamTheta, CamPhi, CamRange))
    x = CamRange * cos(CamTheta * pi / 180)
    y = CamRange * sin(CamTheta * pi / 180)
    lookX = boardHeight * cos(CamTheta * pi / 180)
    lookY = boardHeight * sin(CamTheta * pi / 180)
    lookZ = boardHeight * sin(CamPhi * pi / 180)
    gluLookAt(x, y, boardHeight/2,
              lookX, lookY, lookZ,
              0.0, 0.0, 1.0)


    # 3D
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
    glEnable(GL_LIGHT0)
    # drawAxes(100)

    glLightfv(GL_LIGHT4, GL_POSITION, [0, 0, 2*boardHeight, 1])
    glLightfv(GL_LIGHT4, GL_SPOT_DIRECTION, [0, 0, -1])
    glLightfv(GL_LIGHT4, GL_SPOT_CUTOFF, 45)
    glLightfv(GL_LIGHT4, GL_AMBIENT, [1, 1, 1, 1])
    glEnable(GL_LIGHT4)

    draw_game(friendlyBoard, enemyBoard) # Current board
    glPushMatrix()
    glTranslate(0, -boardHeight/2, 0)
    draw_minions(hand)
    glPopMatrix()
    glDisable(GL_LIGHT4)

    glTranslate(0, boardHeight + sqrt(2)*boardHeight/2, boardHeight/2)
    glRotate(90, 1, 0, 0)

    glLightfv(GL_LIGHT1, GL_POSITION, [0, boardHeight, 0, 1])
    glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, [0, -1, 0])
    glLightfv(GL_LIGHT1, GL_SPOT_CUTOFF, 45)
    glLightfv(GL_LIGHT1, GL_AMBIENT, [0, 1, 0, 1])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0, 1, 0, 1])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0, 1, 0, 1])
    glEnable(GL_LIGHT1)

    draw_game(potentialBoard1["friendly"], potentialBoard1["enemy"]) # Middle board
    glPushMatrix()
    glTranslate(0, boardHeight - 200, 0)
    draw_minions(getPlayed(hand, potentialBoard1['hand']))
    glPopMatrix()
    glDisable(GL_LIGHT1)

    glTranslate(-boardWidth, 0, sqrt(2)*boardHeight/2)
    glRotate(45, 0, 1, 0)

    glLightfv(GL_LIGHT2, GL_POSITION, [0, boardHeight, 0, 1])
    glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, [-1, -1, 0])
    glLightfv(GL_LIGHT2, GL_SPOT_CUTOFF, 45)
    glLightfv(GL_LIGHT2, GL_AMBIENT, [1, 0, 0, 1])
    glLightfv(GL_LIGHT2, GL_DIFFUSE, [1, 0, 0, 1])
    glLightfv(GL_LIGHT2, GL_SPECULAR, [1, 0, 0, 1])
    glEnable(GL_LIGHT2)

    draw_game(potentialBoard2["friendly"], potentialBoard2["enemy"]) # Left board
    glPushMatrix()
    glTranslate(0, boardHeight - 200, 0)
    draw_minions(getPlayed(hand, potentialBoard2['hand']))
    glPopMatrix()
    glDisable(GL_LIGHT2)
    glRotate(-45, 0, 1, 0)
    glTranslate(2*boardWidth, 0, 0)
    glRotate(-45, 0, 1, 0)

    glLightfv(GL_LIGHT3, GL_POSITION, [0, boardHeight, 0, 1])
    glLightfv(GL_LIGHT3, GL_SPOT_DIRECTION, [1, -1, 0])
    glLightfv(GL_LIGHT2, GL_SPOT_CUTOFF, 45)
    glLightfv(GL_LIGHT3, GL_AMBIENT, [0, 0, 1, 1])
    glLightfv(GL_LIGHT3, GL_DIFFUSE, [0, 0, 1, 1])
    glLightfv(GL_LIGHT3, GL_SPECULAR, [0, 0, 1, 1])
    glEnable(GL_LIGHT3)

    draw_game(potentialBoard3["friendly"], potentialBoard3["enemy"]) # Right board
    glPushMatrix()
    glTranslate(0, boardHeight - 200, 0)
    draw_minions(getPlayed(hand, potentialBoard3['hand']))
    glPopMatrix()
    glDisable(GL_LIGHT3)
    glDisable(GL_LIGHT0)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)

    # Render 2D Overlay
    draw_overlay()




    glutSwapBuffers()

    time.sleep(0.01)

def getPlayed(hand, potentialHand):
    resultant = [card['name'] for card in potentialHand]
    played = []
    for card in hand:
        if card['name'] not in resultant:
            played.append(card)
    return played

def KeyPressed(key, x, y):
    global CamPhi, CamTheta, CamRange
    global friendlyBoard, enemyBoard, potentialBoard1, potentialBoard2, potentialBoard3, previousBoard, hand
    global mana
    global CamStep, PhiStep, ThetaStep, TimeRemaining, UpdateFunction, Transitioning

    # 'ord' gives the ascii int code of a character
    # 'chr' gives the character associated to the ascii int code.
    key = ord(key)

    usedKeys = ['a', 's', 'w', 'd', 'q', 'e']
    if key == 27:  # Escape
        glutDestroyWindow(hWindow)
        sys.exit()
    elif 's' in usedKeys and key == ord('S') or key == ord('s'):
        CamPhi -= PhiRate
        if CamPhi < -90:
            CamPhi = -90  # Limit
    elif 'w' in usedKeys and key == ord('W') or key == ord('w'):
        CamPhi += PhiRate
        if CamPhi > 90:
            CamPhi = 90  # Limit
    elif 'a' in usedKeys and key == ord('A') or key == ord('a'):
        CamTheta += ThetaRate
        if CamTheta > 360:
            CamTheta -= 360  # Modulus
    elif 'd' in usedKeys and key == ord('D') or key == ord('d'):
        CamTheta -= ThetaRate
        if CamTheta < 0:
            CamTheta += 360  # Modulus
    elif 'e' in usedKeys and key == ord('E') or key == ord('e'):
        CamRange -= RangeRate
    elif 'q' in usedKeys and key == ord('Q') or key == ord('q'):
        CamRange += RangeRate
    elif ord('1') <= key <= ord('3'):

        previousBoard = {"friendly" : friendlyBoard[:], "enemy" : enemyBoard[:], "hand" : hand[:]}
        mana = min(10, mana + 1)
        TimeRemaining = 2000
        CamStep = (-400 - CamRange) / (TimeRemaining / 100)
        PhiStep = (30 - CamPhi) / (TimeRemaining / 100)
        Transitioning = True
        if key == ord('2'):
            ThetaStep = (90 - CamTheta) / (TimeRemaining / 100)
            UpdateFunction = selected_2
        elif key == ord('1'):
            ThetaStep = (60 - CamTheta) / (TimeRemaining / 100)
            UpdateFunction = selected_1
        elif key == ord('3'):
            ThetaStep = (120 - CamTheta) / (TimeRemaining / 100)
            UpdateFunction = selected_3
        # Redefine potential boards

    elif key == ord('0'):
        # Go backwards
        friendlyBoard = previousBoard["friendly"]
        enemyBoard = previousBoard["enemy"]


def selected_3():
    global friendlyBoard, enemyBoard, hand, potentialBoard1, potentialBoard2, potentialBoard3
    # Third selection
    friendlyBoard = potentialBoard3["friendly"][:]
    enemyBoard = potentialBoard3["enemy"][:]
    hand = potentialBoard3["hand"][:]
    # Next turn
    enemyBoard.append(data.select_minion(minions, "Acolyte of Pain"))
    init_texture(enemyBoard[-1]['name'])
    hand.append(data.select_minion(cards, "Soulfire"))
    init_texture(hand[-1]['name'])
    potentialBoard1 = {"friendly": friendlyBoard[:], "enemy": enemyBoard[:], "hand": hand[:]}
    potentialBoard2 = {"friendly": friendlyBoard[:], "enemy": enemyBoard[:], "hand": hand[:]}
    potentialBoard3 = {"friendly": friendlyBoard[:], "enemy": enemyBoard[:], "hand": hand[:]}


def selected_1():
    global friendlyBoard, enemyBoard, hand, potentialBoard1, potentialBoard2, potentialBoard3
    # Second selection
    friendlyBoard = potentialBoard2["friendly"][:]
    enemyBoard = potentialBoard2["enemy"][:]
    hand = potentialBoard2["hand"][:]
    # Next turn
    enemyBoard.append(data.select_minion(minions, "Acolyte of Pain"))
    init_texture(enemyBoard[-1]['name'])
    hand.append(data.select_minion(cards, "Soulfire"))
    init_texture(hand[-1]['name'])
    potentialBoard1 = {"friendly": friendlyBoard[:], "enemy": enemyBoard[:], "hand": hand[:]}
    potentialBoard1["friendly"].append(data.select_minion(minions, "Imp Gang Boss"))
    index = \
        [i for i in range(len(potentialBoard1["hand"])) if
         potentialBoard1["hand"][i]['name'] == "Imp Gang Boss"][0]
    potentialBoard1["hand"].remove(potentialBoard1["hand"][index])
    index = \
        [i for i in range(len(potentialBoard1["hand"])) if potentialBoard1["hand"][i]['name'] == "Soulfire"][0]
    potentialBoard1["hand"].remove(potentialBoard1["hand"][index])
    index = \
        [i for i in range(len(potentialBoard1["enemy"])) if potentialBoard1["enemy"][i]['name'] == "Acolyte of Pain"][0]
    potentialBoard1["enemy"].remove(potentialBoard1["enemy"][index])
    potentialBoard2 = {"friendly": friendlyBoard[:], "enemy": enemyBoard[:], "hand": hand[:]}
    potentialBoard2["friendly"].append(data.select_minion(minions, "Imp Gang Boss"))
    index = \
        [i for i in range(len(potentialBoard2["hand"])) if potentialBoard2["hand"][i]['name'] == "Imp Gang Boss"][0]
    potentialBoard2["hand"].remove(potentialBoard2["hand"][index])
    index = \
        [i for i in range(len(potentialBoard2["hand"])) if potentialBoard2["hand"][i]['name'] == "Soulfire"][0]
    potentialBoard2["hand"].remove(potentialBoard2["hand"][index])
    potentialBoard3 = {"friendly": friendlyBoard[:], "enemy": enemyBoard[:], "hand": hand[:]}
    index = \
        [i for i in range(len(potentialBoard3["enemy"])) if potentialBoard3["enemy"][i]['name'] == "Acolyte of Pain"][0]
    potentialBoard3["enemy"].remove(potentialBoard3["enemy"][index])
    index = \
        [i for i in range(len(potentialBoard3["friendly"])) if potentialBoard3["friendly"][i]['name'] == "Flame Imp"][0]
    potentialBoard3["friendly"][index] = potentialBoard3["friendly"][index].copy()
    potentialBoard3["friendly"][index]["health"] = 1
    index = \
        [i for i in range(len(potentialBoard3["hand"])) if potentialBoard3["hand"][i]['name'] == "Mortal Coil"][0]
    potentialBoard3["hand"].remove(potentialBoard3["hand"][index])


def selected_2():
    global friendlyBoard, enemyBoard, hand, potentialBoard1, potentialBoard2, potentialBoard3
    # First selection
    friendlyBoard = potentialBoard1["friendly"][:]
    enemyBoard = potentialBoard1["enemy"][:]
    hand = potentialBoard1["hand"][:]
    # Next turn
    enemyBoard.append(data.select_minion(minions, "Acolyte of Pain"))
    init_texture(enemyBoard[-1]['name'])
    hand.append(data.select_minion(cards, "Soulfire"))
    init_texture(hand[-1]['name'])
    potentialBoard1 = {"friendly": friendlyBoard[:], "enemy": enemyBoard[:], "hand": hand[:]}
    potentialBoard1["friendly"].append(data.select_minion(minions, "Imp Gang Boss"))
    potentialBoard1["friendly"].append(data.select_minion(minions, "Flame Imp"))
    potentialBoard1["hand"].remove(potentialBoard1["hand"][0])
    potentialBoard1["hand"].remove(potentialBoard1["hand"][0])
    index = \
        [i for i in range(len(potentialBoard1["friendly"])) if potentialBoard1["friendly"][i]['name'] == "Flame Imp"][0]
    potentialBoard1["friendly"][index] = potentialBoard1["friendly"][index].copy()
    potentialBoard1["friendly"][index]["health"] = 1
    index = \
        [i for i in range(len(potentialBoard1["enemy"])) if potentialBoard1["enemy"][i]['name'] == "Acolyte of Pain"][0]
    potentialBoard1["enemy"].remove(potentialBoard1["enemy"][index])
    potentialBoard2 = {"friendly": friendlyBoard[:], "enemy": enemyBoard[:], "hand": hand[:]}
    potentialBoard2["friendly"].append(data.select_minion(minions, "Imp Gang Boss"))
    potentialBoard2["friendly"].append(data.select_minion(minions, "Flame Imp"))
    potentialBoard2["hand"].remove(potentialBoard2["hand"][0])
    potentialBoard2["hand"].remove(potentialBoard2["hand"][0])
    potentialBoard3 = potentialBoard1


if __name__ == "__main__":
    # Info about the OpenGL version
    # print "GPU                      = ",glGetString(GL_VENDOR)
    # print "Renderer                 = ",glGetString(GL_RENDERER)
    # print "OpenGL                   = ",glGetString(GL_VERSION)

    # Defining global variables
    global hWindow, nWidth, nHeight
    global show_axes, fill_polygons
    global cardback, vertexBuffers

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
    print(CamRange)
    # Read in our data
    cards = data.read_json()
    minions = data.get_minions(cards)

    handNames = ['Knife Juggler', 'Mortal Coil', 'Flame Imp', 'Imp Gang Boss']
    friendlyBoardNames = ['Flame Imp', 'Flame Juggler']
    enemyBoardNames = ['Loot Hoarder']
    hand = [data.select_minion(cards, name) for name in handNames]
    friendlyBoard = [data.select_minion(minions, name) for name in friendlyBoardNames]
    enemyBoard = [data.select_minion(minions, name) for name in enemyBoardNames]
    potentialBoard1 = {"friendly" : friendlyBoard[:], "enemy" : enemyBoard[:], "hand" : hand[:]} # Balanced
    potentialBoard1["friendly"].append(data.select_minion(minions, "Knife Juggler"))
    potentialBoard1["hand"].remove(potentialBoard1["hand"][0]) # Knife Juggler
    potentialBoard1["hand"].remove(potentialBoard1["hand"][0]) # Mortal Coil
    potentialBoard1["enemy"].remove(enemyBoard[0])

    potentialBoard2 = {"friendly" : friendlyBoard[:], "enemy" : enemyBoard[:], "hand" : hand[:]} # Aggro
    potentialBoard2["friendly"].append(data.select_minion(minions, "Knife Juggler"))
    potentialBoard2["hand"].remove(potentialBoard2["hand"][0])
    potentialBoard2["friendly"].append(data.select_minion(minions, "Flame Imp"))
    potentialBoard2["hand"].remove(potentialBoard2["hand"][1])
    if random.randint(0, 1) == 0:
        potentialBoard2["enemy"].remove(potentialBoard2["enemy"][0])

    potentialBoard3 = {"friendly" : friendlyBoard[:], "enemy" : enemyBoard[:], "hand" : hand[:]} # Control
    potentialBoard3["friendly"].append(data.select_minion(minions, "Imp Gang Boss"))
    potentialBoard3["hand"].remove(potentialBoard3["hand"][3])

    potentialBoard3["friendly"][1] = potentialBoard3["friendly"][1].copy()
    potentialBoard3["friendly"][1]["health"] = 1
    potentialBoard3["enemy"].remove(enemyBoard[0])

    for minion in hand:
        init_texture(minion['name'])

    for minion in friendlyBoard:
        init_texture(minion['name'])

    for minion in enemyBoard:
        init_texture(minion['name'])

    cardback = data.load_obj("cardback.obj")
    materials = data.load_mtl("cardback.mtl")

    cardbackVertices = []
    for obj in cardback:
        cardbackVertices.append(vbo.VBO(numpy.array(obj["vertices"], 'f')))

    cardbackNormals = []
    for obj in cardback:
        cardbackNormals.append(vbo.VBO(numpy.array(obj["normals"], 'f')))
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
