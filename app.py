import streamlit as st
import numpy as np
import requests
import json
import os

# API endpoint configurations
API_BASE_URL = "https://stpete2-othello-api.hf.space"  # Hugging Face Space URL

# Add your Hugging Face API token
HF_TOKEN = os.getenv("HF_TOKEN")  # Set this in your environment variables
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

class GameInterface:
    @staticmethod
    def new_game():
        """Start a new game via API"""
        try:
            response = requests.get(f"{API_BASE_URL}/new-game", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to start new game: {str(e)}")
            # Return a default empty board state
            return {
                "board": [[0] * 8 for _ in range(8)],
                "valid_moves": [],
                "winner": None
            }

    @staticmethod
    def make_move(row, col):
        """Make a move via API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/make-move",
                json={"row": row, "col": col},
                headers=HEADERS
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                st.warning("Invalid move. Please try again.")
            else:
                st.error(f"Server error: {str(e)}")
            return st.session_state.game_state
        except Exception as e:
            st.error(f"Error making move: {str(e)}")
            return st.session_state.game_state

    @staticmethod
    def get_valid_moves():
        """Get valid moves via API"""
        try:
            response = requests.get(f"{API_BASE_URL}/valid-moves", headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to get valid moves: {str(e)}")
            return []

# Streamlit UI setup
st.set_page_config(layout="centered", page_title="AI Othello")

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = GameInterface.new_game()
    st.session_state.last_move = None
    st.session_state.ai_last_move = None

def handle_move(i, j):
    """Handle a move at position (i, j)"""
    if st.session_state.game_state["winner"] is None:  # Only allow moves if game isn't over
        new_state = GameInterface.make_move(i, j)
        st.session_state.game_state = new_state
        st.session_state.last_move = (i, j)

# Streamlit interface
st.title("AI Othello")

# Controls container
with st.container():
    col1, col2 = st.columns([2, 2])
    
    with col1:
        st.write("You play as Black (First)")
    
    with col2:
        if st.button("Reset Game", key="reset_button"):
            st.session_state.game_state = GameInterface.new_game()
            st.session_state.last_move = None
            st.session_state.ai_last_move = None

# Game board container
with st.container():
    # Center the board
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        board = np.array(st.session_state.game_state["board"])
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
                    is_valid_move = [i, j] in st.session_state.game_state["valid_moves"]
                    button_style = (
                        "background-color: #4CAF50; color: white;" if is_valid_move 
                        else "background-color: #ffffff;"
                    )
                    
                    # Create a button for each cell
                    st.button(
                        piece,
                        key=f"cell_{i}_{j}",
                        on_click=handle_move,
                        args=(i, j),
                        help=f"Position ({i}, {j})",
                        use_container_width=True
                    )

# Game info container
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        # Score
        black_count = np.sum(board == 1)
        white_count = np.sum(board == -1)
        st.write(f"Score - Black: {black_count}, White: {white_count}")

    with col2:
        # Game status
        winner = st.session_state.game_state["winner"]
        if winner is not None:
            if winner == 1:
                st.success("Black wins!")
            elif winner == -1:
                st.success("White wins!")
            else:
                st.info("It's a tie!")
        
        # Valid moves
        valid_moves = st.session_state.game_state["valid_moves"]
        if valid_moves:
            st.write("Valid moves:", valid_moves)
        else:
            if winner is None:
                st.write("No valid moves available. Turn passes.")

# Add footer with API information
st.markdown("---")
st.markdown("Powered by [stpete2/othello-api](https://huggingface.co/spaces/stpete2/othello-api)")
