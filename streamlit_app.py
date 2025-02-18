
import streamlit as st
import numpy as np
import requests

# API endpoint configuration
API_BASE_URL = "https://stpete2-othello-api.hf.space"  # APIのエンドポイント

class GameInterface:
    @staticmethod
    def new_game():
        """Start a new game via API"""
        try:
            response = requests.get(f"{API_BASE_URL}/new-game")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to start new game: {str(e)}")
            # デフォルトの初期盤面を返す（エラー時の表示用）
            return {
                "board": [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, -1, 1, 0, 0, 0],
                    [0, 0, 0, 1, -1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0]
                ],
                "valid_moves": [[2, 3], [3, 2], [4, 5], [5, 4]],
                "winner": None
            }

    @staticmethod
    def make_move(row, col):
        """Make a move via API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/make-move",
                json={"row": row, "col": col}
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
            response = requests.get(f"{API_BASE_URL}/valid-moves")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to get valid moves: {str(e)}")
            return []

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = GameInterface.new_game()

def handle_move(i, j):
    """Handle a move at position (i, j)"""
    new_state = GameInterface.make_move(i, j)
    st.session_state.game_state = new_state

# Streamlit UI
st.title("API Othello")

# Controls container
with st.container():
    col1, col2 = st.columns([2, 2])
    
    with col1:
        st.write("You play as Black (First)")
    
    with col2:
        if st.button("Reset Game", key="reset_button"):
            st.session_state.game_state = GameInterface.new_game()

# Game board container
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        board = np.array(st.session_state.game_state["board"])
        valid_moves = st.session_state.game_state["valid_moves"]
        
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
                    is_valid_move = [i, j] in valid_moves
                    
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
        if valid_moves:
            st.write("Valid moves:", valid_moves)
        else:
            if winner is None:
                st.write("No valid moves available. Turn passes.")



