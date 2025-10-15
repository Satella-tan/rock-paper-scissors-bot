import random

epsilon = 0.15
moves_count = [0,0,0] # R, P, S
number_of_rounds = 12
move_index = {'R': 0, 'P': 1, 'S': 2}
move_names = {'R': 'Rock', 'P': 'Paper', 'S': 'Scissors'}
print("Winning of a round is +1 point")


def start_game():
    user_score = 0
    bot_score = 0   
    valid_rounds = 0

    while valid_rounds < number_of_rounds:
        n = sum(moves_count) # number of valid moves played

        #empirical probabilities EX.[0.5, 0.3, 0.2]
        if n == 0:
            empirical_prob_moves = [1/3, 1/3, 1/3]
        else:
            empirical_prob_moves = [moves_count[j]/n for j in range(3)]
        
        #calculate expected payoff for each bot move
        expected_utility = [empirical_prob_moves[(j - 1) % 3] for j in range(3)]
        

        #bot moves
        #start random to test the waters
        if valid_rounds>=5:
            bot_move = random.choice(['R','P','S']) 
        elif valid_rounds % 2 == 0:
            if random.random() < epsilon:
                bot_move = random.choice(['R','P','S']) 
            else:
                bot_move = ['R','P','S'][expected_utility.index(max(expected_utility))]
        else:
            bot_move = random.choice(['R','P','S']) 

        #user moves
        user_move = input("What move would you like to play? (R,P,S): ").upper()
        if user_move not in move_index:
            print("Invalid move, please choose R, P or S")
            continue

        print(f"Bot played {move_names[bot_move]}")
        moves_count[move_index[user_move]] += 1
        #score
        
        if user_move == bot_move:
            pass
        elif (user_move == "R" and bot_move == "S") or (user_move == "P" and bot_move == "R") or (user_move == "S" and bot_move == "P"):
            user_score += 1
        else:
            bot_score += 1

        valid_rounds += 1

    print(f"Your score : {user_score} | Bot score : {bot_score}")
    print(f"Your moves :")
    for move, idx in move_index.items():
        print(f"- You played {move_names[move]}: {moves_count[idx]}")        





            
start_game()
