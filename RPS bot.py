import random
import math
from collections import Counter


moves_count_decay = [0,0,0] # R, P, S
deque_temp_moves_count = [] # based on k rounds of memory
moves_count_real = [0,0,0] 
number_of_rounds = 15
move_index = {'R': 0, 'P': 1, 'S': 2}
move_names = {'R': 'Rock', 'P': 'Paper', 'S': 'Scissors'}
print("Winning of a round is +1 point")


def start_game():
    user_score = 0
    bot_score = 0   
    valid_rounds = 0
    a = 0.7        # Smoothing for empirical_prob_moves
    gamma = 0.98   # Decay factor for moves_count_decay (older moves count less)
    k = calculate_recent_rounds(number_of_rounds) # Number of recent rounds for memory
    b = 0.1        # Weight for recent empirical probabilities
    epsilon = 0.15 # Probability for bot to make a random move (ghost emoji)
    empirical_prob_recent = [0,0,0] # R, P, S

    while valid_rounds < number_of_rounds:
        n = sum(moves_count_decay) # number of valid moves played

        # empirical probabilities EX.[0.5, 0.3, 0.2]
        if n == 0:
            empirical_prob_moves = [1/3, 1/3, 1/3]
        else:
            empirical_prob_moves = [(moves_count_decay[j] + a)/(n + 3*a) for j in range(3)]
        print(f"{empirical_prob_moves}")
        # calculate expected payoff for each bot move
        expected_utility_all_time = [empirical_prob_moves[(j - 1) % 3] for j in range(3)]
        expected_utility_recent = [empirical_prob_recent[(j - 1) % 3] for j in range(3)]
        expected_utility = [expected_utility_all_time[ii] + b * expected_utility_recent[ii] for ii in range(3)]
        print(f"Expected utility all time: {expected_utility_all_time}")
        print(f"Expected utility recent: {expected_utility_recent}")
        print(f"Expected utility: {expected_utility}")
        

        # bot moves
        # start random to test the waters
        if valid_rounds>=(round(k/2)):
            bot_move = random.choice(['R','P','S']) 
        # every two moves bot plays based on eu
        elif valid_rounds % 2 == 0:
            if random.random() < epsilon:
                bot_move = random.choice(['R','P','S']) 
            else:
                bot_move = ['R','P','S'][expected_utility.index(max(expected_utility))]
        else:
            bot_move = random.choice(['R','P','S']) 

        # user moves
        # ask the user
        user_move = input("What move would you like to play? (R,P,S): ").upper()
        if user_move not in move_index:
            print("Invalid move, please choose R, P or S")
            continue
        # record last k user moves (Recent moves)

        deque_temp_moves_count.append(user_move)
        print(deque_temp_moves_count)
        if len(deque_temp_moves_count) > k:
            deque_temp_moves_count.pop(0)
        frequency = Counter(deque_temp_moves_count)

        recent_n = len(deque_temp_moves_count)
        recent_counts = [
            frequency.get('R', 0),
            frequency.get('P', 0),
            frequency.get('S', 0),
        ]

        # recent empirical probabilities (no smoothing)
        if recent_n == 0:
            empirical_prob_recent = [0, 0, 0]
        else:
            empirical_prob_recent = [c / recent_n for c in recent_counts]
        print(f"Recent empirical probabilities: {empirical_prob_recent}")


        print(f"Bot played {move_names[bot_move]}")
        moves_count_decay[:] = [gamma * c for c in moves_count_decay]
        moves_count_decay[move_index[user_move]] += 1
        moves_count_real[move_index[user_move]] += 1
        
        # score
        if user_move == bot_move:
            pass
        elif (user_move == "R" and bot_move == "S") or (user_move == "P" and bot_move == "R") or (user_move == "S" and bot_move == "P"):
            user_score += 1
        else:
            bot_score += 1

        valid_rounds += 1
    
    
    # print results
    print(f"Your score : {user_score} | Bot score : {bot_score}")
    print(f"Your moves :")
    for move, idx in move_index.items():
        print(f"- You played {move_names[move]}: {moves_count_real[idx]}")        



# Calculate recent rounds (k)
C = 0.9581989927330705
e = math.e
k_max = 50             

def calculate_recent_rounds(number_of_rounds):
    """
    Calculates the number of 'recent' rounds (k) using logarithmic decay,
    capped at k_max, and rounded to the nearest integer.
    """
    if number_of_rounds <= 0:
        return 0

    # 1. Calculate the Proportion (P) based on logarithmic decay
    # P = C / ln(A + e)
    proportion = C / math.log(number_of_rounds + e)

    # 2. Calculate the Tentative Value (k_tentative)
    # k_tentative = A * P
    k_tentative = number_of_rounds * proportion

    # 3. Apply the Cap (min) and then Round to the nearest integer
    k = round(min(k_tentative, k_max))
    return k

            
start_game()
