from time import sleep
from game import Game
from AI_brain import makeChoice, getInput

game = Game()

while True:
	if game.game_over:
		print("Game Over")
		break
		#game.game_over = False
		#game.reset()

	AI_CHOICE = makeChoice()
	print(getInput(game))
	match AI_CHOICE:
		case 1:
			if not game.game_over:
				game.move_left()
				print("Moved left")
		case 2:
			if not game.game_over:
				game.move_right()
				print("Moved right")
		case 3:
			if not game.game_over:
				game.move_down()
				print("Moved down by own will")
				game.update_score(0, 1)
		case 4:
			if not game.game_over:
				game.rotate()
				print("Rotated")


	sleep(200 / 1000)
	game.move_down()
	print("Moved down by GAME")