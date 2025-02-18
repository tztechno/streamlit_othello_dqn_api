
import streamlit as st
import numpy as np
from othello import OthelloGame, OthelloAI
import torch
import os

# Streamlit UI setup
st.set_page_config(layout="centered", page_title="AI Othello")


# Initialize session state
if 'game' not in st.session_state:
    st.session_state.game = OthelloGame()
    st.session_state.ai = OthelloAI()
    # モデルのロード（HuggingFaceのURLを使用）
    try:
        model_url = "https://huggingface.co/stpete2/dqn_othello_20250216/resolve/main/othello_model.pth"
        st.session_state.ai.load_model(model_url)
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")


def handle_move(i, j):
    """Handle a move at position (i, j)"""
    if 'move_made' not in st.session_state:
        st.session_state.move_made = False
        
    current_player = st.session_state.game.current_player
    human_first = st.session_state.player_color == "Black (First)"
    
    if (human_first and current_player == 1) or (not human_first and current_player == -1):
        if st.session_state.game.is_valid_move(i, j):
            # Make human move
            st.session_state.game.make_move(i, j)
            st.session_state.last_move = (i, j)
            st.session_state.move_made = True
            
            # AI's turn
            valid_moves = st.session_state.game.get_valid_moves()
            if valid_moves:
                action = st.session_state.ai.ai.get_action(
                    st.session_state.game.get_state(),
                    valid_moves,
                    training=False
                )
                if action:
                    st.session_state.game.make_move(*action)
                    st.session_state.ai_last_move = action

# Streamlit interface
st.title("AI Othello")

# Controls container
with st.container():
    col1, col2 = st.columns([2, 2])
    
    with col1:
        # Player selection
        if 'player_color' not in st.session_state:
            st.session_state.player_color = "Black (First)"
        player_color = st.radio("Choose your color:", ["Black (First)", "White (Second)"])
        if player_color != st.session_state.player_color:
            st.session_state.player_color = player_color
            # If player switches to White, let AI make first move
            if player_color == "White (Second)" and st.session_state.game.current_player == 1:
                valid_moves = st.session_state.game.get_valid_moves()
                if valid_moves:
                    action = st.session_state.ai.ai.get_action(
                        st.session_state.game.get_state(),
                        valid_moves,
                        training=False
                    )
                    if action:
                        st.session_state.game.make_move(*action)
                        st.session_state.ai_last_move = action
    
    with col2:
        # Reset button
        if st.button("Reset Game", key="reset_button"):
            st.session_state.game = OthelloGame()
            st.session_state.last_move = None
            st.session_state.ai_last_move = None
            st.session_state.move_made = False
            
            # If AI goes first
            if player_color == "White (Second)":
                valid_moves = st.session_state.game.get_valid_moves()
                if valid_moves:
                    action = st.session_state.ai.ai.get_action(
                        st.session_state.game.get_state(),
                        valid_moves,
                        training=False
                    )
                    if action:
                        st.session_state.game.make_move(*action)
                        st.session_state.ai_last_move = action

# Game board container
with st.container():
    # Center the board
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        board = st.session_state.game.get_state()
        valid_moves = st.session_state.game.get_valid_moves()
        
        # Create board grid
        for i in range(8):
            cols_board = st.columns(8)
            for j in range(8):
                with cols_board[j]:
                    # Determine the piece to display
                    if board[i][j] == 1:
                        piece = "⚫"
                    elif board[i][j] == -1:
                        piece = "⚪"
                    else:
                        piece = "·"
                    
                    # Highlight valid moves
                    is_valid_move = (i, j) in valid_moves
                    
                    # Create a button for each cell
                    st.button(
                        piece,
                        key=f"cell_{i}_{j}",
                        on_click=handle_move,
                        args=(i, j),
                        help=f"Position ({i}, {j})",
                        use_container_width=True,
                        disabled=not is_valid_move
                    )

# Game info container
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        # Score
        black_count = np.sum(board == 1)
        white_count = np.sum(board == -1)
        st.write(f"Score - Black: {black_count}, White: {white_count}")
        
        # Current player
        current_player = "Black" if st.session_state.game.current_player == 1 else "White"
        st.write(f"Current player: {current_player}")
    
    with col2:
        # Game status
        winner = st.session_state.game.get_winner()
        if winner is not None:
            if winner == 1:
                st.success("Black wins!")
            elif winner == -1:
                st.success("White wins!")
            else:
                st.info("It's a tie!")
        
        # Valid moves
        if valid_moves:
            st.write("Valid moves:", valid_moves)
        else:
            if winner is None:
                st.write("No valid moves available. Turn passes.")

# Reset move_made flag if needed
if 'move_made' in st.session_state and st.session_state.move_made:
    st.session_state.move_made = False

# Add debug information
st.markdown("---")
st.write("Debug Information:")
st.write(f"Current Directory: {os.getcwd()}")
st.write(f"Directory Contents: {os.listdir('.')}")




