import json
import numpy


def read_json():
    """
    Read the file, and convert the json to a python format
    :return:
    """
    file = open("C:\\Users\\Aidan\\Dropbox\\University\\COSC3000\ComputerGraphics\\cards.collectible.json")

    cards = json.load(file)

    return cards

def get_minions(cards) -> []:
    """
    Read data from the card data file. Returns a list of {}
    """
    keys = ["cost", "health", "attack", "name", "text"]
    values = [{key: card.get(key, "") for key in keys} for card in cards if card['type'] == 'MINION']
    return values


def get_spells(cards):
    """
    :return: all spells in the game
    """
    keys = ["name", "cost", "text"]
    spells = [{key: card[key] for key in keys} for card in cards if card['type'] == 'SPELL']
    return spells

def select_minion(minions, name:str):
    for minion in minions:
        if minion['name'] == name:
            return minion


def load_obj(filename: str):
    file = open(filename, "r")
    vertices = []
    textures = [[0, 0]]
    normals = []
    faces = []
    objects = []
    object = {} # material, vertices, textures, normals, faces
    for line in file:
        tokens = line.split()
        if tokens[0] == "v":
            vertices.append([float(x) for x in tokens[1:]])
        elif tokens[0] == "vt":
            textures.append([float(x) for x in tokens[1:]])
        elif tokens[0] == "vn":
            normals.append([float(x) for x in tokens[1:]])
        elif tokens[0] == "f":
            faces.append([[int(y) if y != "" else 1 for y in x.split("/")] for x in tokens[1:]])
        elif tokens[0] == "o":
            # New object
            if len(object) > 0:
                object["vertices"] = vertices
                object["textures"] = textures
                object["normals"] = normals
                object["faces"] = faces # Still need to be resolved
                objects.append(object)
            object = {"name" : tokens[1]}
    object["vertices"] = vertices
    object["textures"] = textures
    object["normals"] = normals
    object["faces"] = faces  # Still need to be resolved
    objects.append(object)

    # Resolve faces
    for obj in objects:
        for face in obj["faces"]:
            for i in range(len(face)):
                # Subtract 1 as .obj indices start from 1
                face[i] = (obj["vertices"][face[i][0] - 1],
                           obj["textures"][face[i][1] - 1],
                           obj["normals"][face[i][2] - 1])
    return objects


def get_obj_vertices(faces):
    vertices = numpy.array([[coord[0] for coord in face] for face in faces], float)
    vertices = vertices.flatten()
    return vertices

def load_mtl(filename: str):
    file = open(filename, "r")
    materials = []
    material = {}
    for line in file:
        line = line.strip()
        tokens = line.split()
        if tokens[0] == "newmtl":
            if material != {}:
                materials.append(material)
            material = {"name" : tokens[1]}
        elif tokens[0] == "Ka":
            material["ambient"] = [int(x) for x in tokens[1:4]]
        elif tokens[0] == "Kd":
            material["diffuse"] = [int(x) for x in tokens[1:4]]
        elif tokens[0] == "Ks":
            material["specular"] = [int(x) for x in tokens[1:4]]
    materials.append(material)
    return materials

if __name__ == "__main__":
    cards = read_json()
    minions = get_minions(cards)
    for i in range(5):
        print(minions[i])
    faces = load_obj("C:\\Users\Aidan\Dropbox\\University\COSC3000\ComputerGraphics\cardback.obj")
    for i in range(5):
        print(faces[i])