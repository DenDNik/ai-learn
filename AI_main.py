import pygame,sys
from game_ai import AI_Game
from Model1 import AI
import matplotlib.pyplot as plt

plot_scores = []
plot_mean_scores = []
plot_rewards = []
plot_loss = []
plot_choice_by_model = []
plot_random_choice = []
choice_by_model_count = 0
random_choice_count = 0
plot_average_rewards_per_game = []
plot_average_scores_per_game = []
record = 0
game = AI_Game()
AI = AI()

GAME_UPDATE = pygame.USEREVENT
pygame.time.set_timer(GAME_UPDATE, 200)

while True:
	state_old = AI.getInput(game)
	move_down = False
	action, choice_by_model, random_choice = AI.makeChoice(state_old)
	choice_by_model_count += choice_by_model
	random_choice_count += random_choice
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			AI.policy_net.save_model(file_name="test_model.pth")
			plt.figure(1)
			plt.plot(plot_average_rewards_per_game)
			plt.title("Average reward per game")
			plt.xlabel("Iteration")
			plt.ylabel("Average reward")
			plt.grid()
			plt.show()
			plt.figure(2)
			plt.plot(plot_scores)
			plt.title("Score per game")
			plt.xlabel("Iteration")
			plt.ylabel("Score")
			plt.grid()
			plt.show()
			plt.figure(3)
			plt.plot(plot_loss)
			plt.title("Average loss per game")
			plt.xlabel("Iteration")
			plt.ylabel("Average loss")
			plt.grid()
			plt.show()
			plt.figure(4)
			plt.plot(plot_choice_by_model, label='Choice was made by model')
			plt.plot(plot_random_choice, label='Choice was randomly')
			plt.title("Choice count per game")
			plt.xlabel("Iteration")
			plt.ylabel("Own choices count")
			plt.legend()
			plt.grid()
			plt.show()
			pygame.quit()
			sys.exit()
		if event.type == GAME_UPDATE and game.game_over == False:
			move_down = True

	reward, game_over, score = game.play_step(action, move_down)
	state_new = AI.getInput(game)

	# remember
	AI.remember(state_old, action, reward, state_new, game_over)

	# data for plotting
	plot_rewards.append(reward)
	plot_scores.append(score)

	if game_over == 1:
		gained_scores = game.score
		game.reset()
		AI.numberOfGames += 1
		loss = AI.train()
		if score > record:
			record = score
			AI.policy_net.save_model()
		if AI.numberOfGames % 10 == 0:
			AI.update_target_net()
		AI.updateEpsilon()
		total_game_rewards = 0
		total_score = 0
		plot_loss.append(loss)
		for i in plot_rewards:
			total_game_rewards += i
		total_game_rewards = total_game_rewards / len(plot_rewards)
		for i in plot_scores:
			total_score += i
		if total_game_rewards != -10:
			plot_average_rewards_per_game.append(total_game_rewards)
			plot_scores.append(gained_scores)
			plot_choice_by_model.append(choice_by_model_count)
			plot_random_choice.append(random_choice_count)
		plot_rewards = []
		choice_by_model_count = 0
		random_choice_count = 0


		print(f"Game: {AI.numberOfGames}, Reward: {total_game_rewards}, Score: {score}, Epsilon: {AI.epsilon}")
