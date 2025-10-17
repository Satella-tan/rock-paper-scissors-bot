import random
import math
from collections import Counter

# Constants
MOVE_INDEX = {'R': 0, 'P': 1, 'S': 2}
MOVE_NAMES = {'R': 'Rock', 'P': 'Paper', 'S': 'Scissors'}
C = 0.9581989927330705  # Constant for calculating recent rounds
e = math.e              # Mathematical constant e


class EntropyBot:
    """
    A Rock-Paper-Scissors bot that uses entropy and softmax decision making
    to adapt to the player's strategy.
    """
    
    def __init__(self, rounds=15):
        self.name = "EntropyBot"
        self.rounds = rounds
        
        # Bot parameters
        self.a = 0.7        # Smoothing for empirical probabilities
        self.b = 0.2        # Weight for recent empirical probabilities
        self.gamma = 0.98   # Decay factor for moves_count_decay
        self.beta_max = 5.0  # Maximum inverse temperature for softmax
        
        # State tracking
        self.moves_count_decay = [0, 0, 0]  # R, P, S with decay
        self.moves_count_real = [0, 0, 0]   # R, P, S absolute count
        self.deque_temp_moves_count = []    # Recent moves memory
        self.empirical_prob_recent = [0, 0, 0]  # Recent empirical probabilities
        
        # Calculate memory length
        self.k = self.calculate_recent_rounds(rounds)
    
    def calculate_recent_rounds(self, amount):
        """
        Calculates the number of 'recent' rounds (k) using logarithmic decay.
        """
        if amount <= 0:
            return 0

        # Calculate the proportion based on logarithmic decay
        proportion = C / math.log(amount + e)
        
        # Calculate the value and round to nearest integer
        k_tentative = amount * proportion
        k = round(k_tentative)
        
        return k
    
    def decide_move(self, valid_rounds):
        # Decide the next move based on the current game state.
        
        # Probability for bot to make a random move (ghost emoji)
        epsilon = max(0.1, 0.25 * (1 - valid_rounds / self.rounds))
        
        # empirical probabilities EX.[0.5, 0.3, 0.2]
        n = sum(self.moves_count_real)
        if n == 0:
            empirical_prob_moves = [1/3, 1/3, 1/3]
        else:
            empirical_prob_moves = [(self.moves_count_decay[j] + self.a)/(n + 3*self.a) for j in range(3)]
        print(f"{empirical_prob_moves}")
        
        # calculate entropy
        entropy = -sum(p * math.log2(p) for p in empirical_prob_moves if p > 0)
        Hmax = math.log(3, 2)
        
        # calculate expected payoff for each bot move
        expected_utility_all_time = [empirical_prob_moves[(j - 1) % 3] for j in range(3)]
        expected_utility_recent = [self.empirical_prob_recent[(j - 1) % 3] for j in range(3)]
        expected_utility = [expected_utility_all_time[ii] + self.b * expected_utility_recent[ii] for ii in range(3)]
        print(f"Expected utility all time: {expected_utility_all_time}")
        print(f"Expected utility recent: {expected_utility_recent}")
        print(f"Expected utility: {expected_utility}")
        
        # start random to test the waters
        if valid_rounds < (round(self.k/2)):
            bot_move = random.choice(['R', 'P', 'S'])
        # sometimes go random to explore
        elif random.random() < epsilon:
            bot_move = random.choice(['R', 'P', 'S'])
        # use entropy-based softmax for decision making
        else:
            # map entropy to inverse temperature beta
            beta = self.beta_max * (Hmax - entropy) / Hmax
            print(f"Beta (inverse temperature): {beta:.3f}")
            
            # compute expected utility for each move
            probs = empirical_prob_moves
            EU = [
                probs[2] - probs[1],  # Rock wins Scissors, loses to Paper
                probs[0] - probs[2],  # Paper wins Rock, loses to Scissors
                probs[1] - probs[0]   # Scissors wins Paper, loses to Rock
            ]
            print(f"EU for [R, P, S]: {EU}")
            
            # softmax to get adaptive action probabilities
            maxEU = max(EU)
            expEU = [math.exp(beta * (u - maxEU)) for u in EU]
            Z = sum(expEU)
            softmax_probs = [x / Z for x in expEU]
            print(f"Softmax probabilities: {softmax_probs}")
            
            # sample a move using those probabilities
            r = random.random()
            cumulative = 0
            bot_move = 'S'  # should never be the case
            for j, p in enumerate(softmax_probs):
                cumulative += p
                if r < cumulative:
                    bot_move = ['R', 'P', 'S'][j]
                    break
            print("Bot strategy: Entropy-based softmax")
        
        return bot_move
    
    def update_state(self, user_move):
        """
        Update the bot's internal state based on the user's move.
        """
        # Update recent moves memory
        self.deque_temp_moves_count.append(user_move)
        print(self.deque_temp_moves_count)
        if len(self.deque_temp_moves_count) > self.k:
            self.deque_temp_moves_count.pop(0)
        
        # Calculate recent move frequencies
        frequency = Counter(self.deque_temp_moves_count)
        recent_n = len(self.deque_temp_moves_count)
        recent_counts = [
            frequency.get('R', 0),
            frequency.get('P', 0),
            frequency.get('S', 0),
        ]
        
        # Update recent empirical probabilities
        if recent_n == 0:
            self.empirical_prob_recent = [0, 0, 0]
        else:
            self.empirical_prob_recent = [c / recent_n for c in recent_counts]
        print(f"Recent empirical probabilities: {self.empirical_prob_recent}")
        
        # Update move counts with decay
        self.moves_count_decay[:] = [self.gamma * c for c in self.moves_count_decay]
        self.moves_count_decay[MOVE_INDEX[user_move]] += 1
        self.moves_count_real[MOVE_INDEX[user_move]] += 1


class Game:
    """
    Manages a Rock-Paper-Scissors game between a bot and a human player.
    """
    
    def __init__(self, bot, rounds=15):
        self.bot = bot
        self.rounds = rounds
        self.user_score = 0
        self.bot_score = 0
        self.valid_rounds = 0
    
    def play_round(self):
        """
        Play a single round of the game.
        """
        # Bot decides its move
        bot_move = self.bot.decide_move(self.valid_rounds)
        
        # Get user move
        user_move = input("What move would you like to play? (R,P,S): ").upper()
        if user_move not in MOVE_INDEX:
            print("Invalid move, please choose R, P or S")
            return False
        
        # Update bot's state
        self.bot.update_state(user_move)
        
        # Display bot's move
        print(f"Bot played {MOVE_NAMES[bot_move]}")
        
        # Calculate scores
        if user_move == bot_move:
            # Tie, no score change
            pass
        elif ((user_move == "R" and bot_move == "S") or 
              (user_move == "P" and bot_move == "R") or 
              (user_move == "S" and bot_move == "P")):
            self.user_score += 1
        else:
            self.bot_score += 1
        
        self.valid_rounds += 1
        return True
    
    def play_game(self):
        """
        Play a complete game.
        """
        print("Winning of a round is +1 point")
        
        while self.valid_rounds < self.rounds:
            round_valid = self.play_round()
            if not round_valid:
                continue
        
        # Print final results
        print(f"Your score : {self.user_score} | Bot score : {self.bot_score}")
        print(f"Your moves :")
        for move, idx in MOVE_INDEX.items():
            print(f"- You played {MOVE_NAMES[move]}: {self.bot.moves_count_real[idx]}")


# Main execution
if __name__ == "__main__":
    rounds = int(input("How many rounds would you like to play? "))
    bot = EntropyBot(rounds)
    game = Game(bot, rounds)
    game.play_game()
