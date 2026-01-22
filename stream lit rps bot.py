import streamlit as st
import math
import pandas as pd
from rock_paper_scissors_entropy_bot import EntropyBot, Game, MOVE_INDEX, MOVE_NAMES

st.set_page_config(layout="wide", page_title="RPS Entropy Bot", initial_sidebar_state="collapsed")

def play_round(user_move):
    """Play a single round when a button is clicked"""
    if st.session_state.game.valid_rounds < st.session_state.game.rounds:
        # Use the Game's play_round method, which handles:
        # - Bot deciding move
        # - Recording user move via bot.update_state()
        # - Calculating scores
        # - Incrementing valid_rounds
        bot_move, result = st.session_state.game.play_round(user_move)
        
        # Convert result to display string
        if result == "tie":
            result_display = "Tie."
            result_type = "tie"
        elif result == "user_win":
            result_display = "You win."
            result_type = "win"
        else:  # bot_win
            result_display = "You lose."
            result_type = "lose"
        
        # Store for display
        st.session_state.last_bot_move = bot_move
        st.session_state.last_result = result_display
        st.session_state.last_result_type = result_type
        
        st.rerun()

# Title will be in the center panel

# Initialize game settings
if 'rounds' not in st.session_state:
    st.session_state.rounds = 15
if 'game' not in st.session_state:
    st.session_state.game = None
if 'bot' not in st.session_state:
    st.session_state.bot = None
if 'last_bot_move' not in st.session_state:
    st.session_state.last_bot_move = None
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'last_result_type' not in st.session_state:
    st.session_state.last_result_type = None
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

# Custom CSS 
st.markdown("""

""", unsafe_allow_html=True)

with open('./style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Game setup
if not st.session_state.game_started:
    col_left, col_center, col_right = st.columns([1, 1.5, 1], gap="large")
    with col_center:
        st.markdown("""
        <div style="margin-top: 80px;"></div>
        <div class="game-title">RPS - Entropy Bot</div>
        <div style="margin-bottom: 40px;"></div>
        """, unsafe_allow_html=True)
        rounds_input = st.number_input("Rounds", min_value=1, max_value=1000, value=35)
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        if st.button("Start Game", type="secondary", use_container_width=True):
            st.session_state.rounds = rounds_input
            st.session_state.bot = EntropyBot(rounds_input)
            st.session_state.game = Game(st.session_state.bot, rounds_input)
            st.session_state.game_started = True
            st.session_state.user_score = 0
            st.session_state.bot_score = 0
            st.rerun()
        st.markdown("""
        <div class="hint-text">Bot adapting to your strategy</div>
        """, unsafe_allow_html=True)

# main game interface
if st.session_state.game_started:
    # check if game is over
    if st.session_state.game.valid_rounds >= st.session_state.game.rounds:
        col_left, col_center, col_right = st.columns([1, 1.2, 1], gap="large")
        
        # Left panel - Stats
        with col_left:
            st.markdown('<div class="section-title"># Belief / <span class="highlight">Information</span></div>', unsafe_allow_html=True)
            bot = st.session_state.bot
            counts = bot.moves_count_real if bot else [0, 0, 0]
            total = sum(counts) if counts else 0
            
            # Move distribution table
            table_html = '''
            <table class="stats-table">
                <tr><th>Move</th><th>Count</th><th>Freq</th></tr>
            '''
            for move in ['R', 'P', 'S']:
                idx = MOVE_INDEX[move]
                val = counts[idx]
                freq = 0 if total == 0 else val / total
                table_html += f'<tr><td>{MOVE_NAMES[move]}</td><td class="cyan">{val}</td><td class="gray">{freq:.3f}</td></tr>'
            table_html += '</table>'
            st.markdown(table_html, unsafe_allow_html=True)
            
            st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
            
            # Entropy display
            if bot:
                n = sum(bot.moves_count_real)
                if n == 0:
                    empirical = [1/3, 1/3, 1/3]
                else:
                    empirical = [(bot.moves_count_decay[j] + bot.a) / (n + 3*bot.a) for j in range(3)]
                H = -sum(p * math.log2(p) for p in empirical if p > 0)
                Hmax = math.log2(3)
                norm = H / Hmax if Hmax > 0 else 0.0
                pct = int(norm * 100)
                
                interp = (
                    "Highly predictable" if H < 0.60 else
                    "Moderately predictable" if H < 0.90 else
                    "Somewhat random" if H < 1.20 else
                    "Mostly random"
                )
                
                entropy_html = f'''
                <div class="entropy-row">
                    <span class="entropy-label">Entropy</span>
                    <div class="entropy-bar-container"><div class="entropy-bar" style="width:{pct}%;"></div></div>
                    <span class="entropy-value">{H:.2f} bits</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #666666; margin-top: 5px;">{interp}</div>
                '''
                st.markdown(entropy_html, unsafe_allow_html=True)
            
            # Move history
            if bot:
                history = " → ".join(bot.deque_temp_moves_count) if bot.deque_temp_moves_count else "No moves yet"
                st.markdown(f'<div class="move-history">{history}</div>', unsafe_allow_html=True)
        
        # Center panel - Game Over
        with col_center:
            user_score = st.session_state.game.user_score
            bot_score = st.session_state.game.bot_score
            
            if user_score > bot_score:
                outcome = "You Win!"
                outcome_color = "#538d4e"
            elif bot_score > user_score:
                outcome = "Bot Wins"
                outcome_color = "#c9453a"
            else:
                outcome = "It's a Tie"
                outcome_color = "#888888"
            
            st.markdown(f'''
            <div class="game-title">Game Over</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 48px; font-weight: 700; text-align: center; color: {outcome_color}; margin: 30px 0;">{outcome}</div>
            <div class="score-display">You <span class="score-value">{user_score}</span> — Bot <span class="score-value">{bot_score}</span></div>
            ''', unsafe_allow_html=True)
            
            # Final stats table
            st.markdown('''
            <table class="stats-table" style="margin: 20px auto; max-width: 300px;">
                <tr><th>Your Move</th><th>Count</th></tr>
            ''', unsafe_allow_html=True)
            for move, idx in MOVE_INDEX.items():
                count = st.session_state.bot.moves_count_real[idx]
                st.markdown(f'<tr><td>{MOVE_NAMES[move]}</td><td class="cyan">{count}</td></tr>', unsafe_allow_html=True)
            st.markdown('</table>', unsafe_allow_html=True)
            
            st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
            if st.button("Play Again", type="secondary", use_container_width=True):
                st.session_state.game_started = False
                st.session_state.game = None
                st.session_state.bot = None
                st.session_state.last_bot_move = None
                st.session_state.last_result = None
                st.session_state.last_result_type = None
                st.rerun()
            st.markdown('<div class="hint-text">Thanks for playing!</div>', unsafe_allow_html=True)
    else:
        # Result color mapping
        result_colors = {
            'win': '#538d4e',   # green
            'lose': '#c9453a',  # red
            'tie': '#888888'    # neutral gray
        }
        
        # Main layout with columns
        col_left, col_center, col_right = st.columns([1, 1.5, 1], gap="large")
        
        # Left panel - Belief/Information
        with col_left:
            st.markdown('<div class="section-title"># Belief / <span class="highlight">Information</span></div>', unsafe_allow_html=True)
            bot = st.session_state.bot
            counts = bot.moves_count_real if bot else [0, 0, 0]
            total = sum(counts) if counts else 0
            
            # Move distribution table
            table_html = '''
            <table class="stats-table">
                <tr><th>Move</th><th>Count</th><th>Freq</th></tr>
            '''
            for move in ['R', 'P', 'S']:
                idx = MOVE_INDEX[move]
                val = counts[idx]
                freq = 0 if total == 0 else val / total
                table_html += f'<tr><td>{MOVE_NAMES[move]}</td><td class="cyan">{val}</td><td class="gray">{freq:.3f}</td></tr>'
            table_html += '</table>'
            st.markdown(table_html, unsafe_allow_html=True)
            
            st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
            
            # Entropy display
            if bot:
                n = sum(bot.moves_count_real)
                if n == 0:
                    empirical = [1/3, 1/3, 1/3]
                else:
                    empirical = [(bot.moves_count_decay[j] + bot.a) / (n + 3*bot.a) for j in range(3)]
                H = -sum(p * math.log2(p) for p in empirical if p > 0)
                Hmax = math.log2(3)
                norm = H / Hmax if Hmax > 0 else 0.0
                pct = int(norm * 100)
                
                interp = (
                    "Highly predictable" if H < 0.60 else
                    "Moderately predictable" if H < 0.90 else
                    "Somewhat random" if H < 1.20 else
                    "Mostly random"
                )
                
                entropy_html = f'''
                <div class="entropy-row">
                    <span class="entropy-label">Entropy</span>
                    <div class="entropy-bar-container"><div class="entropy-bar" style="width:{pct}%;"></div></div>
                    <span class="entropy-value">{H:.2f} bits</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #666666; margin-top: 5px;">{interp}</div>
                '''
                st.markdown(entropy_html, unsafe_allow_html=True)
            
            # Move history
            if bot:
                history = " → ".join(bot.deque_temp_moves_count) if bot.deque_temp_moves_count else "No moves yet"
                st.markdown(f'<div class="move-history">{history}</div>', unsafe_allow_html=True)

        # Center panel - Main game
        with col_center:
            # Title
            st.markdown('<div class="game-title">RPS - Entropy Bot</div>', unsafe_allow_html=True)
            
            # Round indicator
            current_round = st.session_state.game.valid_rounds + 1
            total_rounds = st.session_state.game.rounds
            st.markdown(f'<div class="round-indicator">Round {current_round} / {total_rounds}</div>', unsafe_allow_html=True)
            
            # Score display
            user_score = st.session_state.game.user_score
            bot_score = st.session_state.game.bot_score
            st.markdown(f'<div class="score-display">You <span class="score-value">{user_score}</span> — Bot <span class="score-value">{bot_score}</span></div>', unsafe_allow_html=True)
            
            # Bot Move (giant white letter) or placeholder
            if st.session_state.last_bot_move:
                bot_move_letter = st.session_state.last_bot_move
                st.markdown(f'<div class="bot-move">{bot_move_letter}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="bot-move-placeholder">Bot move appears here</div>', unsafe_allow_html=True)
            
            # Result text
            if st.session_state.last_result:
                result_class = f"result-{st.session_state.last_result_type}"
                st.markdown(f'<div class="result-text {result_class}">{st.session_state.last_result}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-text" style="color: #444444;">Make your move</div>', unsafe_allow_html=True)
            
            # Player input buttons (R P S)
            btn_col1, btn_col2, btn_col3 = st.columns(3, gap="medium")
            
            with btn_col1:
                if st.button("R", key="rock", type="secondary", use_container_width=True):
                    play_round('R')
            
            with btn_col2:
                if st.button("P", key="paper", type="secondary", use_container_width=True):
                    play_round('P')
            
            with btn_col3:
                if st.button("S", key="scissors", type="secondary", use_container_width=True):
                    play_round('S')

            # Footer text
            st.markdown('<div class="hint-text">Bot adapts to your strategy</div>', unsafe_allow_html=True)
        
        # Right panel - Bot strategy info
        
        # with col_right:
        #     st.markdown('<div class="section-title">Bot <span class="highlight">Strategy</span></div>', unsafe_allow_html=True)
            
        #     if bot:
        #         # Show bot parameters
        #         params_html = f'''
        #         <table class="stats-table">
        #             <tr><th>Parameter</th><th>Value</th></tr>
        #             <tr><td>Memory (k)</td><td class="cyan">{bot.k}</td></tr>
        #             <tr><td>Smoothing (a)</td><td class="cyan">{bot.a}</td></tr>
        #             <tr><td>Recent weight (b)</td><td class="cyan">{bot.b}</td></tr>
        #             <tr><td>Decay (γ)</td><td class="cyan">{bot.gamma}</td></tr>
        #             <tr><td>β max</td><td class="cyan">{bot.beta_max}</td></tr>
        #         </table>
        #         '''
        #         st.markdown(params_html, unsafe_allow_html=True)
                
        #         st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
                
        #         # Recent probabilities
        #         if sum(bot.empirical_prob_recent) > 0:
        #             recent_html = '''
        #             <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #666666; margin-bottom: 10px;">Recent probs:</div>
        #             '''
        #             for i, move in enumerate(['R', 'P', 'S']):
        #                 prob = bot.empirical_prob_recent[i]
        #                 pct = int(prob * 100)
        #                 recent_html += f'''
        #                 <div class="prob-row">
        #                     <span class="prob-label">{move}</span>
        #                     <div class="prob-bar-container"><div class="prob-bar" style="width:{pct}%;"></div></div>
        #                     <span class="prob-value">{prob:.2f}</span>
        #                 </div>
        #                 '''
        #             st.markdown(recent_html, unsafe_allow_html=True)

