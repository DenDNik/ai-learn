# imports
import numpy as np
import torch
import  torch.optim as optim
import torch.nn as nn
from collections import deque
import torch.nn.functional as F
import os
import random

MAX_MEMORY = 10_000
BATCH_SIZE = 1000
DISCOUNT = 0.99
EPS_START = 1
EPS_END = 0.05
EPS_DECAY = 0.9
LR = 0.0001

class NeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save_model(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class AI:
    def __init__(self):
        self.numberOfGames = 0
        self.epsilon = EPS_START
        self.memory = deque(maxlen=MAX_MEMORY)
        self.policy_net = NeuralNetwork(400, 256, 4)
        self.target_net = NeuralNetwork(400, 256, 4)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=LR)
        self.criterion = nn.MSELoss()

    def getInput(self, obj):
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

    def train_model(self, state, action, reward, next_state, game_over):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)


        Q_value = self.policy_net(state).gather(1, action)
        target = self.target_net(state).gather(1, action)
        for idx in range(len(game_over)):
            Q_new = reward[idx]
            if not game_over[idx]:
                Q_new = reward[idx] + DISCOUNT * torch.max(self.target_net(next_state[idx]))
            target[idx][torch.argmax(action).item()] = Q_new
        loss = self.criterion(Q_value, target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def update_target_net(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())



    def train(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        loss = self.train_model(states, actions, rewards, next_states, game_overs)
        return loss

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def makeChoice(self, state):
        # random moves: tradeoff exploration / exploitation
        choice_by_model = 0
        random_choice = 0
        final_move = [0,0,0,0]
        if random.random() < self.epsilon:
            random_choice = 1
            move = random.randint(0,3)
            final_move[move] = 1
        else:
            choice_by_model = 1
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.policy_net(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move, choice_by_model, random_choice

    def updateEpsilon(self):
        self.epsilon = max(EPS_END, self.epsilon * EPS_DECAY)