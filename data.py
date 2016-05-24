import json


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
    Read data from the card data file. Returns a list of (mana, health, attack)
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

def select_minion(minions, name):
    for minion in minions:
        if minion['name'] == name:
            return minion

if __name__ == "__main__":
    cards = read_json()
    minions = get_minions(cards)
    for i in range(5):
        print(minions[i])