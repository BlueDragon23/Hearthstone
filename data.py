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
    keys = ["cost", "health", "attack", "name", "text", "type"]
    values = [{key: card.get(key, "") for key in keys} for card in cards if card['type'] == 'MINION']
    return values


def get_spells(cards):
    """
    :return: all spells in the game
    """
    keys = ["name", "cost", "text", "type"]
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
        elif tokens[0] == "usemtl":
            object["material"] = tokens[1]
        elif tokens[0] == "o":
            # New object
            if len(object) > 0:
                object["faces"] = faces # Still need to be resolved
                objects.append(object)
            object = {"name" : tokens[1]}
            faces = []
    object["faces"] = faces  # Still need to be resolved
    objects.append(object)

    # Resolve faces
    for obj in objects:
        for face in obj["faces"]:
            for i in range(len(face)):
                # Subtract 1 as .obj indices start from 1
                face[i] = (vertices[face[i][0] - 1],
                           textures[face[i][1] - 1],
                           normals[face[i][2] - 1])
        obj["vertices"] = get_obj_vertices(obj["faces"])
        obj["normals"] = get_obj_normals(obj["faces"])
    return objects


def get_obj_vertices(faces):
    vertices = numpy.array([[coord[0] for coord in face] for face in faces], float)
    vertices = vertices.flatten()
    return vertices

def get_obj_normals(faces):
    normals = numpy.array([[coord[2] for coord in face] for face in faces], float)
    normals = normals.flatten()
    return normals

def load_mtl(filename: str):
    file = open(filename, "r")
    materials = []
    material = {}
    for line in file:
        line = line.strip()
        tokens = line.split()
        if len(tokens) == 0:
            continue
        if tokens[0] == "newmtl":
            if material != {}:
                materials.append(material)
            material = {"name" : tokens[1]}
        elif tokens[0] == "Ka":
            material["ambient"] = [float(x) for x in tokens[1:4]]
        elif tokens[0] == "Kd":
            material["diffuse"] = [float(x) for x in tokens[1:4]]
        elif tokens[0] == "Ks":
            material["specular"] = [float(x) for x in tokens[1:4]]
    materials.append(material)
    return materials

def find_mtl(name: str, materials):
    for material in materials:
        if material["name"] == name:
            return material

if __name__ == "__main__":
    cards = read_json()
    minions = get_minions(cards)
    for i in range(5):
        print(minions[i])
    faces = load_obj("C:\\Users\Aidan\Dropbox\\University\COSC3000\ComputerGraphics\cardback.obj")
    for i in range(5):
        print(faces[i])