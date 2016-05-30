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



# Globals
CamPhi = 30
CamTheta = 90
CamRange = 0
InnerRadius = 0
PerspectiveAngle = 45
MaximumDataPoint = 0
cardback = []
vertexBuffers = 0
boardWidth = 3080
boardHeight = 1400

# Textures
textureIds = []
BoardId = 0
BoardImage = None
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
    # TODO: Set perspective
    gluPerspective(PerspectiveAngle, float(nWidth) / float(nHeight), 0.1, 10000.0)
    glMatrixMode(GL_MODELVIEW)


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
        draw_status_bars(minion)
        glPopMatrix()


def draw_card():
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

def draw_game(friendlyMinions, enemyMinions):
    glPushMatrix()
    draw_minions(friendlyMinions)
    glPushMatrix()
    glTranslate(0, 500, 0)
    draw_minions(enemyMinions)
    glPopMatrix()
    glPushMatrix()
    glTranslate(boardWidth/2 - 500, 0, -250)
    glRotate(90, 0, 0, 1)
    glRotate(90, 1, 0, 0)
    for _ in range(5):
        draw_cardback()
        glTranslate(0, 0, 20)
    glTranslate(-boardHeight/4, 0, -20*5)
    for _ in range(5):
        draw_cardback()
        glTranslate(0, 0, 20)
    glPopMatrix()
    glTranslate(0, -100, -10)
    draw_board()
    glPopMatrix()

def DrawGLScene():
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
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1])
    glEnable(GL_LIGHT0)
    # drawAxes(100)

    glLightfv(GL_LIGHT4, GL_POSITION, [0, 0, 2*boardHeight, 1])
    glLightfv(GL_LIGHT4, GL_SPOT_DIRECTION, [0, 0, -1])
    glLightfv(GL_LIGHT4, GL_SPOT_CUTOFF, 45)
    glLightfv(GL_LIGHT4, GL_AMBIENT, [1, 1, 1, 1])
    glEnable(GL_LIGHT4)

    draw_game(friendlyBoard, enemyBoard) # Current board
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
    glDisable(GL_LIGHT3)
    glDisable(GL_LIGHT0)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)

    # Render 2D Overlay
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    gluOrtho2D(0, width, 0, height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    def draw_square(x, y, size):
        """
        Treats the top left corner as 0, 0
        """
        glColor([0.8*x for x in [1, 1, 1]])
        glBegin(GL_QUADS)
        glVertex2f(x, height - y)
        glVertex2f(x, height - y - size)
        glVertex2f(x+size, height - y - size)
        glVertex2f(x+size, height - y)
        glEnd()
    size = 50
    margin = 10
    draw_square(0, 0, size)
    glColor(0, 0, 0)
    glBegin(GL_LINE_STRIP)
    glVertex2f(size/2, height - margin)
    glVertex2f(size/2, height - (size - margin))
    glEnd()
    draw_square(width/2 - size/2, 0, size)
    glColor(0, 0, 0)
    glBegin(GL_LINE_STRIP)
    glVertex2f(width/2 - size/2 + margin, height - margin)
    glVertex2f(width/2 + size/2 - margin, height - margin) # -
    glVertex2f(width/2 + size/2 - margin, height - size/2) # |
    glVertex2f(width/2 - size/2 + margin, height - size/2) # -
    glVertex2f(width/2 - size/2 + margin, height - size + margin) # |
    glVertex2f(width/2 + size/2 - margin, height - size + margin) # -
    glEnd()
    draw_square(width - size, 0, size)
    glColor(0, 0, 0)
    glBegin(GL_LINE_STRIP)
    glVertex2f(width - size + margin, height - margin)
    glVertex2f(width - margin, height - margin) # -
    glVertex2f(width - margin, height - size/2) # |
    glVertex2f(width - size + margin, height - size/2) # -
    glVertex2f(width - margin, height - size/2) # -
    glVertex2f(width - margin, height - size + margin) # |
    glVertex2f(width - (size - margin), height - size + margin) # -
    glEnd()
    glPopMatrix()



    glutSwapBuffers()

    time.sleep(0.01)


def KeyPressed(key, x, y):
    global CamPhi, CamTheta, CamRange
    global friendlyBoard, enemyBoard, potentialBoard1, potentialBoard2, potentialBoard3, previousBoard

    # 'ord' gives the ascii int code of a character
    # 'chr' gives the character associated to the ascii int code.
    key = ord(key)

    usedKeys = ['a', 's', 'w', 'd', 'q', 'e']
    if key == 27:  # Escape
        glutDestroyWindow(hWindow)
        sys.exit()
    elif 's' in usedKeys and key == ord('S') or key == ord('s'):
        CamPhi -= 2
        if CamPhi < -90:
            CamPhi = -90  # Limit
    elif 'w' in usedKeys and key == ord('W') or key == ord('w'):
        CamPhi += 2
        if CamPhi > 90:
            CamPhi = 90  # Limit
    elif 'a' in usedKeys and key == ord('A') or key == ord('a'):
        CamTheta += 3
        if CamTheta > 360:
            CamTheta -= 360  # Modulus
    elif 'd' in usedKeys and key == ord('D') or key == ord('d'):
        CamTheta -= 3
        if CamTheta < 0:
            CamTheta += 360  # Modulus
    elif 'e' in usedKeys and key == ord('E') or key == ord('e'):
        CamRange -= 50
    elif 'q' in usedKeys and key == ord('Q') or key == ord('q'):
        CamRange += 50
    elif key == ord('1'):
        # First selection
        previousBoard = {"friendly" : friendlyBoard, "enemy" : enemyBoard}
        friendlyBoard = potentialBoard1["friendly"]
        enemyBoard = potentialBoard1["enemy"]
    elif key == ord('2'):
        # Second selection
        previousBoard = {"friendly" : friendlyBoard, "enemy" : enemyBoard}
        friendlyBoard = potentialBoard2["friendly"]
        enemyBoard = potentialBoard2["enemy"]
    elif key == ord('3'):
        # Third selection
        previousBoard = {"friendly" : friendlyBoard, "enemy" : enemyBoard}
        friendlyBoard = potentialBoard3["friendly"]
        enemyBoard = potentialBoard3["enemy"]


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

    # Read in our data
    cards = data.read_json()
    minions = data.get_minions(cards)

    friendlyBoard = [minions[i] for i in range(20, 24)]
    friendlyBoard[0]['health'] = 5
    enemyBoard = [minions[i] for i in range(50, 53)]
    potentialBoard1 = {"friendly" : friendlyBoard, "enemy" : enemyBoard}
    potentialBoard2 = {"friendly" : friendlyBoard, "enemy" : enemyBoard}
    potentialBoard3 = {"friendly" : friendlyBoard, "enemy" : enemyBoard}

    for minion in friendlyBoard:
        init_texture(minion['name'])

    for minion in enemyBoard:
        init_texture(minion['name'])

    cardback = data.load_obj("C:\\Users\Aidan\Dropbox\\University\COSC3000\ComputerGraphics\cardback.obj")
    materials = data.load_mtl("C:\\Users\Aidan\Dropbox\\University\COSC3000\ComputerGraphics\cardback.mtl")

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
    # glutMouseFunc(handler)

    # Tell people how to exit, then start the program...
    print("To quit: Select OpenGL display window with mouse, then press ESC key.")

    InitGL(nWidth, nHeight)

    # enter the window's main loop to set things rolling
    glutMainLoop()
