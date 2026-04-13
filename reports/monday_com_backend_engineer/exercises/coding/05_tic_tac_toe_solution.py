"""
Exercise 5: Tic Tac Toe Game - SOLUTION
=========================================
Difficulty: Medium | Monday.com Real Interview Question
LeetCode Equivalent: #348 Design Tic-Tac-Toe

Time Complexity:  O(1) per move for win checking
Space Complexity: O(n^2) for the board + O(n) for row/col sums
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
    Tic Tac Toe with O(1) win detection using sum tracking.

    Core idea: Assign X = +1 and O = -1. Maintain running sums for each row,
    column, and both diagonals. A player wins when the absolute value of any
    sum equals n (meaning one player filled that entire line).
    """

    def __init__(self, n: int = 3):
        self.n = n
        # The board stores "X", "O", or None for display and occupied checks
        self.board: list[list[Optional[str]]] = [[None] * n for _ in range(n)]

        # O(1) win detection: track sums per row, per column, and diagonals
        # X contributes +1, O contributes -1
        # A sum of +n means X filled the line, -n means O filled it
        self.row_sums: list[int] = [0] * n
        self.col_sums: list[int] = [0] * n
        self.diag_sum: int = 0       # Main diagonal (row == col)
        self.anti_diag_sum: int = 0  # Anti-diagonal (row + col == n - 1)

        # Game state tracking
        self.move_count: int = 0
        self.state: GameState = GameState.IN_PROGRESS

    def make_move(self, row: int, col: int, player: str) -> GameState:
        """
        Place a mark and check for win/draw in O(1).
        """
        # --- Validation ---
        if self.state != GameState.IN_PROGRESS:
            raise ValueError("Game is already over")

        if not (0 <= row < self.n and 0 <= col < self.n):
            raise ValueError(f"Position ({row}, {col}) is out of bounds")

        if self.board[row][col] is not None:
            raise ValueError(f"Cell ({row}, {col}) is already occupied")

        expected_player = "X" if self.move_count % 2 == 0 else "O"
        if player != expected_player:
            raise ValueError(f"It's {expected_player}'s turn, not {player}'s")

        # --- Place the mark ---
        self.board[row][col] = player
        self.move_count += 1

        # Map player to delta: X = +1, O = -1
        delta = 1 if player == "X" else -1

        # --- Update sums ---
        self.row_sums[row] += delta
        self.col_sums[col] += delta

        if row == col:
            self.diag_sum += delta

        if row + col == self.n - 1:
            self.anti_diag_sum += delta

        # --- Check for win (O(1)) ---
        # A line is won when its absolute sum equals n
        if (
            abs(self.row_sums[row]) == self.n
            or abs(self.col_sums[col]) == self.n
            or abs(self.diag_sum) == self.n
            or abs(self.anti_diag_sum) == self.n
        ):
            self.state = GameState.X_WINS if player == "X" else GameState.O_WINS
            return self.state

        # --- Check for draw ---
        if self.move_count == self.n * self.n:
            self.state = GameState.DRAW
            return self.state

        return GameState.IN_PROGRESS

    def get_board(self) -> list[list[Optional[str]]]:
        """Return the current board state."""
        return self.board

    def get_state(self) -> GameState:
        """Return the current game state."""
        return self.state

    def __str__(self) -> str:
        """Pretty-print the board."""
        lines = []
        for row in self.board:
            cells = [cell if cell is not None else "." for cell in row]
            lines.append(" | ".join(cells))
        separator = "-" * (self.n * 4 - 3)
        return f"\n{separator}\n".join(lines)


# ---------------------------------------------------------------------------
# COMPLEXITY ANALYSIS
# ---------------------------------------------------------------------------
#
# make_move:
#   Time:  O(1) -- constant number of array accesses and comparisons
#   Space: O(1) per call -- no additional allocation
#
# Overall space:
#   O(n^2) for the board (needed for display and occupancy checking)
#   O(n)   for row_sums and col_sums arrays
#   O(1)   for the two diagonal sums
#   Total: O(n^2)
#
# Comparison with naive approach:
#   Naive: O(n) per move -- scan the row, column, and diagonals of the last move
#   Naive: O(n^2) per move if scanning the entire board
#   Our approach: O(1) per move -- constant time regardless of board size
#
# ---------------------------------------------------------------------------
# WHAT INTERVIEWERS LOOK FOR
# ---------------------------------------------------------------------------
#
# 1. O(1) WIN CHECKING: This is the key insight. If you scan the board after
#    each move, you'll get O(n) at best. The sum-tracking approach is O(1).
#    Interviewers specifically test whether you know this optimization.
#
# 2. CLEAN OOP DESIGN: The game should be a class with clear methods.
#    State should be encapsulated. The board representation and win-checking
#    mechanism should be separate concerns.
#
# 3. INPUT VALIDATION: Checking bounds, occupancy, turn order, and game-over
#    state. Many candidates skip validation -- don't. It shows attention to
#    correctness and production-quality thinking.
#
# 4. ENUM FOR STATE: Using an Enum (not string literals or magic numbers)
#    for game state. Shows Python proficiency and type safety awareness.
#
# 5. EDGE CASES: 1x1 board, first move wins (trivially), draw detection,
#    moves after game ends. Mention these proactively.
#
# ---------------------------------------------------------------------------
# COMMON INTERVIEWER FOLLOW-UPS
# ---------------------------------------------------------------------------
#
# Q: "How would you extend this to support n-in-a-row on an m x m board?"
#    (e.g., Connect Four, Gomoku)
# A: The sum-tracking trick no longer gives O(1) because you need to check
#    if any contiguous n cells in a line belong to the same player. Options:
#    - Track running sums in sliding windows along rows/cols/diags: O(1) per move
#    - Maintain direction-based counters at each cell: O(1) per move but O(m^2) space
#    - For Connect Four specifically: only need to check around the last piece
#
# Q: "How would you add an undo/redo feature?"
# A: Use a move history stack. Undo pops the last move, reverses the delta
#    on the relevant sums, clears the cell, decrements move_count, and
#    reverts game state. Redo pushes from a redo stack. This is O(1) per
#    undo/redo operation.
#
# Q: "How would you add AI (computer player)?"
# A: - Minimax algorithm with alpha-beta pruning for optimal play
#    - For 3x3, the game tree is small enough for exhaustive search
#    - For larger boards, use heuristic evaluation functions
#    - Mention that 3x3 tic-tac-toe is a solved game (perfect play = draw)
#
# Q: "How would you make this multiplayer over a network?"
# A: - Separate game state (server) from UI (client)
#    - Server validates all moves and broadcasts state updates
#    - Use WebSockets for real-time communication
#    - Handle disconnections, reconnections, timeouts
#    - At Monday.com specifically: they'd likely use their existing
#      real-time infrastructure (WebSocket/Socket.io for board updates)
#
# Q: "How would you persist game state?"
# A: - Serialize: JSON with board state, move history, current player
#    - Store in Redis for active games (fast read/write)
#    - Archive to PostgreSQL for completed games (analytics, replay)
#    - Event sourcing: store moves, reconstruct state on demand
#
# ---------------------------------------------------------------------------
# ALTERNATIVE APPROACHES
# ---------------------------------------------------------------------------
#
# 1. Bitmask approach (for standard 3x3):
#    - Represent each player's positions as a 9-bit integer
#    - Pre-compute all 8 winning patterns as bitmasks
#    - Win check: (player_bits & pattern) == pattern
#    - O(1) per move, very fast but doesn't generalize to n x n
#
# 2. Magic square approach:
#    - Map cells to a 3x3 magic square (all rows/cols/diags sum to 15)
#    - Track which numbers each player has claimed
#    - A player wins if any 3 of their numbers sum to 15
#    - Elegant but harder to generalize
#
# 3. Naive O(n) scanning:
#    - After each move, scan the row, column, and diagonal(s) of that move
#    - Simple to implement but suboptimal
#    - Acceptable if the interviewer doesn't push for optimization
#    - Still much better than O(n^2) full board scan
