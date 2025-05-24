import numpy as np

from grid import Grid
from colors import Colors
from blocks import *
import random
import pygame

pygame.init()

title_font = pygame.font.Font(None, 40)
score_surface = title_font.render("Score", True, Colors.white)
next_surface = title_font.render("Next", True, Colors.white)
game_over_surface = title_font.render("GAME OVER", True, Colors.white)

score_rect = pygame.Rect(320, 55, 170, 60)
next_rect = pygame.Rect(320, 215, 170, 180)

screen = pygame.display.set_mode((500, 620))
pygame.display.set_caption("Python Tetris")

clock = pygame.time.Clock()

class AI_Game:
	def __init__(self):
		self.grid = Grid()
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.get_random_block()
		self.next_block = self.get_random_block()
		self.game_over = False
		self.score = 0
		self.height = 0


	def update_score(self, lines_cleared, move_down_points):
		if lines_cleared > 0:
			self.score += 100*lines_cleared
		self.score += move_down_points

	def get_random_block(self):
		if len(self.blocks) == 0:
			self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		block = random.choice(self.blocks)
		self.blocks.remove(block)
		return block

	def move_left(self):
		self.current_block.move(0, -1)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(0, 1)

	def move_right(self):
		self.current_block.move(0, 1)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(0, -1)

	def move_down(self):
		rows_cleared = 0
		self.current_block.move(1, 0)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(-1, 0)
			rows_cleared = self.lock_block()
		return rows_cleared

	def lock_block(self):
		tiles = self.current_block.get_cell_positions()
		for position in tiles:
			self.grid.grid[position.row][position.column] = self.current_block.id
		self.current_block = self.next_block
		self.next_block = self.get_random_block()
		rows_cleared = self.grid.clear_full_rows()
		if rows_cleared > 0:
			self.update_score(rows_cleared, 0)
		if self.block_fits() == False:
			self.game_over = True
		return rows_cleared

	def reset(self):
		self.grid.reset()
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.get_random_block()
		self.next_block = self.get_random_block()
		self.score = 0

	def block_fits(self):
		tiles = self.current_block.get_cell_positions()
		for tile in tiles:
			if self.grid.is_empty(tile.row, tile.column) == False:
				return False
		return True

	def rotate(self):
		self.current_block.rotate()
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.undo_rotation()


	def block_inside(self):
		tiles = self.current_block.get_cell_positions()
		for tile in tiles:
			if self.grid.is_inside(tile.row, tile.column) == False:
				return False
		return True

	def draw(self, screen):
		self.grid.draw(screen)
		self.current_block.draw(screen, 11, 11)

		if self.next_block.id == 3:
			self.next_block.draw(screen, 255, 290)
		elif self.next_block.id == 4:
			self.next_block.draw(screen, 255, 280)
		else:
			self.next_block.draw(screen, 270, 270)

	def draw_screen(self):
		# Drawing
		score_value_surface = title_font.render(str(self.score), True, Colors.white)

		screen.fill(Colors.dark_blue)
		screen.blit(score_surface, (365, 20, 50, 50))
		screen.blit(next_surface, (375, 180, 50, 50))

		if self.game_over == True:
			screen.blit(game_over_surface, (320, 450, 50, 50))

		pygame.draw.rect(screen, Colors.light_blue, score_rect, 0, 10)
		screen.blit(score_value_surface, score_value_surface.get_rect(centerx=score_rect.centerx,
																	  centery=score_rect.centery))
		pygame.draw.rect(screen, Colors.light_blue, next_rect, 0, 10)
		self.draw(screen)

		pygame.display.update()

	def getReward(self):
		reward = 0.0
		reward += self.getPunishFromHeight() + self.getRewardFromWidth()
		return reward

	def getPunishFromHeight(self):
		reward = 0.0
		tiles = self.current_block.get_cell_positions()
		grid = np.array(self.grid.grid)
		for position in tiles:
			grid[position.row][position.column] = 0
		h = self.checkHeight(grid)
		if h > 5:
			reward -= 2 * h
		return reward

	def checkHeight(self, grid):
		h = 0
		for x in range(10):
			for y in range(20):
				if grid[y][x] > 0:
					new_h = 20 - y
					h = max(h, new_h)
					break
		return h

	def getRewardFromWidth(self):
		reward = 0.0
		current_block_position = self.current_block.get_cell_positions()
		grid = np.array(self.grid.grid)
		k = 0.9
		for position in current_block_position:
			grid[position.row][position.column] = 0
		for row in range(20):
			number_of_filled_cells = 0
			for column in range(10):
				if grid[19-row][9-column] > 0:
					number_of_filled_cells += 1
			reward += 5*k*number_of_filled_cells
			k *= 0.9

		return reward


	def play_step(self, action, move_down):
		reward = 0
		rows_cleared = 0
		game_over = 0
		if self.game_over:
			reward -= 10
			game_over = 1
			self.game_over = False
		if np.array_equal(action, [1,0,0,0]) and not self.game_over:
			self.move_left()
		if np.array_equal(action, [0,1,0,0]) and not self.game_over:
			self.move_right()
		if np.array_equal(action, [0,0,1,0]) and not self.game_over:
			rows_cleared = self.move_down()
		if np.array_equal(action, [0,0,0,1]) and not self.game_over:
			self.rotate()

		if move_down and not self.game_over:
			rows_cleared = self.move_down()

		self.draw_screen()
		clock.tick(60)

		reward += self.getReward()
		reward += 100*rows_cleared
		return reward, game_over, self.score