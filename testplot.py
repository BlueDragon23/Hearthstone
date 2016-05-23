import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json

file = open("C:\\Users\Aidan\Dropbox\\University\COSC3000\ComputerGraphics\cards.collectible.json")

cards = json.load(file)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

mana = []
health = []
attack = []
for card in cards:
    if card['type'] != 'MINION':
        continue
    mana.append(card['cost'])
    health.append(card['health'])
    attack.append(card['attack'])

ax.scatter(mana, health, attack)
ax.set_xlabel('Mana')
ax.set_ylabel('Health')
ax.set_zlabel('Attack')

plt.show()