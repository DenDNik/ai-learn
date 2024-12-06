from random import randint
from game import Game
import numpy as np


class AI:
    def __int__(self):
        pass


def getInput(obj: Game):
    tiles = obj.current_block.get_cell_positions()
    gridWithoutCurrentBlock = np.array(obj.grid.grid)
    gridWithOnlyCurrentBlock = np.array([[0 for j in range(10)] for i in range(20)])
    for position in tiles:
        gridWithoutCurrentBlock[position.row][position.column] = 0
        gridWithOnlyCurrentBlock[position.row][position.column] = obj.current_block.id
    input = np.append(gridWithoutCurrentBlock, gridWithOnlyCurrentBlock)
    for i in range(0,len(input)):
        if input[i] > 0:
            input[i] = 1

    return input

def makeChoice():
    return randint(1,4)
