import streamlit as st
import math
import pandas as pd
from rock_paper_scissors_entropy_bot import EntropyBot, Game, MOVE_INDEX, MOVE_NAMES

st.set_page_config(layout="wide")

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
<style>
/* Prevent scrolling */
.stApp {
    background-color: #0E1117;
    overflow: hidden;
}
.main .block-container {
    max-width: 100%;
    padding-top: 2rem;
    padding-bottom: 2rem;
}
/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Title styling */
.game-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 23px;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #E5E7EB;
    text-align: center;
    margin-bottom: 8px;
    text-transform: uppercase;
}

/* Round indicator */
.round-indicator {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 15px;
    font-weight: 400;
    color: #9CA3AF;
    text-align: center;
    margin-bottom: 40px;
}

/* Bot move letter */
.bot-move {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 140px;
    font-weight: 800;
    text-align: center;
    line-height: 1;
    margin: 30px 0 20px 0;
    color: #E5E7EB;
    min-height: 140px;
}

/* Placeholder text for bot move */
.bot-move-placeholder {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 16px;
    font-weight: 400;
    color: #6B7280;
    text-align: center;
    margin: 30px 0 20px 0;
    min-height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Result text */
.result-text {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 28px;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-align: center;
    margin: 20px 0 40px 0;
    min-height: 40px;
}

/* Button styling */
button[kind="secondary"] {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif; 
    font-size: 48px !important;
    font-weight: 600 !important;
    background-color: #111827 !important;
    border: 1px solid #374151 !important;
    color: #E5E7EB !important;
    border-radius: 6px !important;
    padding: 30px !important;
    height: auto !important;
    min-height: 90px !important;
    transition: all 0.2s ease !important;
}

button[kind="secondary"]:hover {
    background-color: #1F2937 !important;
    border-color: #4B5563 !important;
}

button[kind="secondary"]:active {
    background-color: #111827 !important;
}

.rps-buttons button[kind="secondary"] {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 720px !important;
    font-weight: 700 !important;
}

/* Subtle hint text */
.hint-text {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 12px;
    color: #9CA3AF;
    text-align: center;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# Game setup
if not st.session_state.game_started:
    col_left, col_center, col_right = st.columns([1, 2, 1], gap="medium")
    with col_center:
        st.markdown("""
        <div class="game-title">RPS - ENTROPY BOT</div>
        """, unsafe_allow_html=True)
        rounds_input = st.number_input("How many rounds would you like to play?", min_value=1, max_value=1000, value=35)
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
        col_left, col_center, col_right = st.columns([1, 1, 1])
        with col_left:
            st.markdown("""
            <div class="game-title">Belief / Information</div>
            <h4> User past moves </h4>
            """, unsafe_allow_html=True)
            bot = st.session_state.bot
            counts = bot.moves_count_real if bot else [0, 0, 0]
            total = sum(counts) if counts else 0
            labels = [MOVE_NAMES['R'], MOVE_NAMES['P'], MOVE_NAMES['S']]
            bars_html = "<div style='display:flex; flex-direction:column; gap:8px;'>"
            for i, label in enumerate(labels):
                val = counts[i]
                pct = 0 if total == 0 else int(100 * val / total)
                bars_html += f"<div style='display:flex; align-items:center; gap:10px;'><div style='width:90px; color:#9CA3AF;'>{label}</div><div style='flex:1; background:#1F2937; border:1px solid #374151; border-radius:4px; height:18px;'><div style='width:{pct}%; height:100%; background:#3B82F6;'></div></div><div style='width:40px; text-align:right; color:#9CA3AF;'>{val}</div></div>"
            bars_html += "</div>"
            st.markdown(bars_html, unsafe_allow_html=True)
            
            # Entropy meter
            if bot:
                n = sum(bot.moves_count_real)
                if n == 0:
                    empirical = [1/3, 1/3, 1/3]
                else:
                    empirical = [(bot.moves_count_decay[j] + bot.a) / (n + 3*bot.a) for j in range(3)]
                H = -sum(p * math.log2(p) for p in empirical if p > 0)
                Hmax = math.log2(3)
                norm = H / Hmax if Hmax > 0 else 0.0
                st.progress(int(norm * 100))
                color = "#3B82F6" if H < 0.90 else "#9CA3AF"
                interp = (
                    "Highly predictable" if H < 0.62 else
                    "Moderately predictable" if H < 0.92 else
                    "Somewhat random" if H < 1.22 else
                    "Mostly random"
                )
                st.markdown(f"<div style=\"color:{color};\">Entropy: {H:.2f} / {Hmax:.2f} bits<br/>Interpretation: {interp}</div>", unsafe_allow_html=True)
            
            # Move history (compact)
            if bot:
                history = " \u2192 ".join(bot.deque_temp_moves_count) if bot.deque_temp_moves_count else "No moves yet"
                st.markdown(f"<div style='font-family: \"JetBrains Mono\", \"IBM Plex Mono\", \"Courier New\", monospace; background:#0F172A; border:1px solid #334155; border-radius:6px; padding:10px; color:#E5E7EB;'>{history}</div>", unsafe_allow_html=True)
            
        
        
        
        with col_center:
            st.markdown("""
            <div class="game-title">RPS - ENTROPY BOT</div>
            """, unsafe_allow_html=True)
            st.header("Game Over!")
            st.write(f"**Final Score:** You {st.session_state.game.user_score} - Bot {st.session_state.game.bot_score}")
            st.write("**Your moves breakdown:**")
            for move, idx in MOVE_INDEX.items():
                count = st.session_state.bot.moves_count_real[idx]
                st.write(f"- {MOVE_NAMES[move]}: {count}")
            if st.button("Play Again", type="secondary", use_container_width=True):
                st.session_state.game_started = False
                st.session_state.game = None
                st.session_state.bot = None
                st.session_state.last_bot_move = None
                st.session_state.last_result = None
                st.session_state.last_result_type = None
                st.rerun()
            st.markdown("""
            <div class="hint-text">Bot adapting to your strategy</div>
            """, unsafe_allow_html=True)
    else:
        # Result color mapping
        result_colors = {
            'win': '#22C55E',   # green
            'lose': '#EF4444',  # red
            'tie': '#9CA3AF'    # neutral gray
        }
        

        
        # Main layout with columns [1,2,1]
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_left:
            st.markdown("""
            <div class="game-title">Belief / Information</div>
            <h4> User past moves </h4>
            """, unsafe_allow_html=True)
            bot = st.session_state.bot
            counts = bot.moves_count_real if bot else [0, 0, 0]
            total = sum(counts) if counts else 0
            labels = [MOVE_NAMES['R'], MOVE_NAMES['P'], MOVE_NAMES['S']]
            bars_html = "<div style='display:flex; flex-direction:column; gap:8px;'>"
            for i, label in enumerate(labels):
                val = counts[i]
                pct = 0 if total == 0 else int(100 * val / total)
                bars_html += f"<div style='display:flex; align-items:center; gap:10px;'><div style='width:90px; color:#9CA3AF;'>{label}</div><div style='flex:1; background:#1F2937; border:1px solid #374151; border-radius:4px; height:18px;'><div style='width:{pct}%; height:100%; background:#3B82F6;'></div></div><div style='width:40px; text-align:right; color:#9CA3AF;'>{val}</div></div>"
            bars_html += "</div>"
            st.markdown(bars_html, unsafe_allow_html=True)
            
            # Entropy meter
            if bot:
                n = sum(bot.moves_count_real)
                if n == 0:
                    empirical = [1/3, 1/3, 1/3]
                else:
                    empirical = [(bot.moves_count_decay[j] + bot.a) / (n + 3*bot.a) for j in range(3)]
                H = -sum(p * math.log2(p) for p in empirical if p > 0)
                Hmax = math.log2(3)
                norm = H / Hmax if Hmax > 0 else 0.0
                st.progress(int(norm * 100))
                color = "#3B82F6" if H < 0.90 else "#9CA3AF"
                interp = (
                    "Highly predictable" if H < 0.60 else
                    "Moderately predictable" if H < 0.90 else
                    "Somewhat random" if H < 1.20 else
                    "Mostly random"
                )
                st.markdown(f"<div style=\"color:{color};\">Entropy: {H:.2f} / {Hmax:.2f} bits<br/>Interpretation: {interp}</div>", unsafe_allow_html=True)
            
            # Move history (compact)
            if bot:
                history = " \u2192 ".join(bot.deque_temp_moves_count) if bot.deque_temp_moves_count else "No moves yet"
                st.markdown(f"<div style='font-family: \"JetBrains Mono\", \"IBM Plex Mono\", \"Courier New\", monospace; background:#0F172A; border:1px solid #334155; border-radius:6px; padding:10px; color:#E5E7EB;'>{history}</div>", unsafe_allow_html=True)
            
            
            





        with col_center:
            # Title
            st.markdown("""
            <div class="game-title">RPS - ENTROPY BOT</div>
            """, unsafe_allow_html=True)
            
            # Round indicator
            current_round = st.session_state.game.valid_rounds + 1
            total_rounds = st.session_state.game.rounds
            st.markdown(f"""
            <div class="round-indicator">Round {current_round} / {total_rounds}</div>
            """, unsafe_allow_html=True)
            
            # Bot Move (giant white letter) or placeholder
            if st.session_state.last_bot_move:
                bot_move_letter = st.session_state.last_bot_move
                st.markdown(f"""
                <div class="bot-move">{bot_move_letter}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="bot-move-placeholder">Bot moves will appear here</div>
                """, unsafe_allow_html=True)
            
            # Result text
            if st.session_state.last_result:
                result_color = result_colors.get(st.session_state.last_result_type, '#9CA3AF')
                st.markdown(f"""
                <div class="result-text" style="color: {result_color};">{st.session_state.last_result}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-text"></div>
                """, unsafe_allow_html=True)
            
            # Player input buttons (R P S)
            st.markdown('<div class="rps-buttons">', unsafe_allow_html=True)
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            
            with btn_col1:
                if st.button("R", key="rock", type="secondary", use_container_width=True):
                    play_round('R')
            
            with btn_col2:
                if st.button("P", key="paper", type="secondary", use_container_width=True):
                    play_round('P')
            
            with btn_col3:
                if st.button("S", key="scissors", type="secondary", use_container_width=True):
                    play_round('S')
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.sidebar.checkbox("Show belief model", value=True)


            # Footer text
            st.markdown("""
            <div class="hint-text">Bot adapting to your strategy (Not yet because i lowk fk up the code)</div>
            """, unsafe_allow_html=True)
        
       





