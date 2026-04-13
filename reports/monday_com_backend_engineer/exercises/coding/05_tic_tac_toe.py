"""
Exercise 5: Tic Tac Toe Game
==============================
Difficulty: Medium | Monday.com Real Interview Question
LeetCode Equivalent: #348 Design Tic-Tac-Toe

PROBLEM:
Design and implement a Tic Tac Toe game for two players on an n x n board.

Requirements:
1. Players take turns placing their mark (X or O) on empty cells
2. After each move, determine if that move wins the game
3. Detect draws (board full, no winner)
4. Reject invalid moves (out of bounds, cell already occupied, game already over)
5. Achieve O(1) win checking per move (not O(n) or O(n^2))

EXAMPLE:
    game = TicTacToe(3)
    game.make_move(0, 0, "X")  # X plays top-left
    game.make_move(1, 1, "O")  # O plays center
    game.make_move(0, 1, "X")  # X plays top-center
    game.make_move(2, 2, "O")  # O plays bottom-right
    game.make_move(0, 2, "X")  # X plays top-right -> X wins! (top row)

KEY INSIGHT FOR O(1) WIN CHECK:
    Instead of scanning the entire board after each move, track running sums
    for each row, column, and diagonal. Assign +1 for X and -1 for O.
    A row/col/diag is won when its absolute sum equals n.

CONSTRAINTS:
- Board size n is between 1 and 100
- Players alternate turns (X always goes first)
- A move is (row, col, player) where player is "X" or "O"
"""

from enum import Enum
from typing import Optional


class GameState(Enum):
    IN_PROGRESS = "in_progress"
    X_WINS = "x_wins"
    O_WINS = "o_wins"
    DRAW = "draw"


class TicTacToe:
    """
    A Tic Tac Toe game with O(1) win detection per move.
    """

    def __init__(self, n: int = 3):
        """
        Initialize the game board.

        Args:
            n: Size of the board (n x n). Default is 3.
        """
        self.n = n
        # TODO: Initialize data structures for:
        #   - The board itself (for display and occupied-cell checking)
        #   - Row sums, column sums, diagonal sums (for O(1) win checking)
        #   - Game state tracking (whose turn, is game over, move count)
        pass

    def make_move(self, row: int, col: int, player: str) -> GameState:
        """
        Place a mark on the board and return the resulting game state.

        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            player: "X" or "O"

        Returns:
            GameState: The state of the game after this move

        Raises:
            ValueError: If the move is invalid (out of bounds, cell occupied,
                       wrong player's turn, or game already over)
        """
        # TODO: Validate the move
        # TODO: Place the mark on the board
        # TODO: Update row/col/diagonal sums
        # TODO: Check for win condition (O(1)!)
        # TODO: Check for draw condition
        # TODO: Return the game state
        pass

    def get_board(self) -> list[list[Optional[str]]]:
        """Return the current board state as a 2D list."""
        # TODO: Return the board
        pass

    def get_state(self) -> GameState:
        """Return the current game state."""
        # TODO: Return current state
        pass

    def __str__(self) -> str:
        """Pretty-print the board for debugging."""
        # TODO: Optional but helpful for debugging
        pass


# ---------------------------------------------------------------------------
# Tests (run with: pytest 05_tic_tac_toe.py -v)
# ---------------------------------------------------------------------------
import pytest


class TestInitialization:
    """Tests for game initialization."""

    def test_default_board_size(self):
        """Default board should be 3x3."""
        game = TicTacToe()
        assert game.n == 3
        board = game.get_board()
        assert len(board) == 3
        assert all(len(row) == 3 for row in board)

    def test_custom_board_size(self):
        """Should support custom board sizes."""
        game = TicTacToe(5)
        assert game.n == 5
        board = game.get_board()
        assert len(board) == 5

    def test_initial_state(self):
        """Game should start in progress."""
        game = TicTacToe()
        assert game.get_state() == GameState.IN_PROGRESS

    def test_empty_board(self):
        """All cells should be None initially."""
        game = TicTacToe()
        board = game.get_board()
        for row in board:
            for cell in row:
                assert cell is None


class TestMakeMove:
    """Tests for making moves."""

    def test_valid_first_move(self):
        """First move by X should be accepted."""
        game = TicTacToe()
        result = game.make_move(0, 0, "X")
        assert result == GameState.IN_PROGRESS
        assert game.get_board()[0][0] == "X"

    def test_alternating_turns(self):
        """Players should alternate: X, O, X, O..."""
        game = TicTacToe()
        game.make_move(0, 0, "X")
        game.make_move(1, 1, "O")
        assert game.get_board()[0][0] == "X"
        assert game.get_board()[1][1] == "O"

    def test_wrong_turn_raises(self):
        """Playing out of turn should raise ValueError."""
        game = TicTacToe()
        game.make_move(0, 0, "X")
        with pytest.raises(ValueError):
            game.make_move(1, 1, "X")  # Should be O's turn

    def test_occupied_cell_raises(self):
        """Playing on an occupied cell should raise ValueError."""
        game = TicTacToe()
        game.make_move(0, 0, "X")
        with pytest.raises(ValueError):
            game.make_move(0, 0, "O")

    def test_out_of_bounds_raises(self):
        """Playing outside the board should raise ValueError."""
        game = TicTacToe()
        with pytest.raises(ValueError):
            game.make_move(3, 0, "X")
        with pytest.raises(ValueError):
            game.make_move(0, -1, "X")


class TestWinConditions:
    """Tests for win detection."""

    def test_x_wins_row(self):
        """X wins by completing a row."""
        game = TicTacToe()
        game.make_move(0, 0, "X")
        game.make_move(1, 0, "O")
        game.make_move(0, 1, "X")
        game.make_move(1, 1, "O")
        result = game.make_move(0, 2, "X")  # Top row complete
        assert result == GameState.X_WINS

    def test_o_wins_column(self):
        """O wins by completing a column."""
        game = TicTacToe()
        game.make_move(0, 0, "X")
        game.make_move(0, 1, "O")
        game.make_move(1, 0, "X")
        game.make_move(1, 1, "O")
        game.make_move(2, 2, "X")
        result = game.make_move(2, 1, "O")  # Middle column complete
        assert result == GameState.O_WINS

    def test_x_wins_main_diagonal(self):
        """X wins via the main diagonal (top-left to bottom-right)."""
        game = TicTacToe()
        game.make_move(0, 0, "X")
        game.make_move(0, 1, "O")
        game.make_move(1, 1, "X")
        game.make_move(0, 2, "O")
        result = game.make_move(2, 2, "X")  # Main diagonal complete
        assert result == GameState.X_WINS

    def test_o_wins_anti_diagonal(self):
        """O wins via the anti-diagonal (top-right to bottom-left)."""
        game = TicTacToe()
        game.make_move(1, 0, "X")
        game.make_move(0, 2, "O")
        game.make_move(2, 2, "X")
        game.make_move(1, 1, "O")
        game.make_move(0, 0, "X")
        result = game.make_move(2, 0, "O")  # Anti-diagonal complete
        assert result == GameState.O_WINS

    def test_move_after_win_raises(self):
        """No moves should be allowed after a win."""
        game = TicTacToe()
        game.make_move(0, 0, "X")
        game.make_move(1, 0, "O")
        game.make_move(0, 1, "X")
        game.make_move(1, 1, "O")
        game.make_move(0, 2, "X")  # X wins
        with pytest.raises(ValueError):
            game.make_move(2, 2, "O")


class TestDraw:
    """Tests for draw detection."""

    def test_draw_game(self):
        """A full board with no winner should be a draw."""
        game = TicTacToe()
        # Classic draw pattern:
        # X O X
        # X X O
        # O X O
        game.make_move(0, 0, "X")
        game.make_move(0, 1, "O")
        game.make_move(0, 2, "X")
        game.make_move(1, 2, "O")
        game.make_move(1, 0, "X")
        game.make_move(2, 0, "O")
        game.make_move(1, 1, "X")
        game.make_move(2, 2, "O")
        result = game.make_move(2, 1, "X")
        assert result == GameState.DRAW


class TestLargeBoard:
    """Tests for larger board sizes."""

    def test_4x4_win(self):
        """Win detection should work on a 4x4 board."""
        game = TicTacToe(4)
        # X fills first row
        for col in range(4):
            game.make_move(0, col, "X")
            if col < 3:
                game.make_move(1, col, "O")  # O plays second row
        # After X's 4th move in row 0, X should win
        assert game.get_state() == GameState.X_WINS

    def test_1x1_instant_win(self):
        """A 1x1 board should be won on the first move."""
        game = TicTacToe(1)
        result = game.make_move(0, 0, "X")
        assert result == GameState.X_WINS


# ---------------------------------------------------------------------------
# HINTS (reveal progressively if stuck)
# ---------------------------------------------------------------------------

# HINT 1: For O(1) win checking, maintain arrays: row_sums[n], col_sums[n],
#          and two ints: diag_sum, anti_diag_sum. Map X -> +1, O -> -1.
#          After each move, update the relevant sum(s) and check if |sum| == n.

# HINT 2: A move at (row, col) affects:
#          - row_sums[row] always
#          - col_sums[col] always
#          - diag_sum only if row == col
#          - anti_diag_sum only if row + col == n - 1
#          Check each affected sum for |sum| == n.

# HINT 3: For turn validation, track move_count. If move_count is even, it's
#          X's turn; if odd, it's O's turn. For draw detection, check if
#          move_count == n * n after a non-winning move.

# ---------------------------------------------------------------------------
# COMPLEXITY TARGETS
# ---------------------------------------------------------------------------
# make_move: O(1) time, O(1) space per call
# Space overall: O(n^2) for the board + O(n) for row/col sums
