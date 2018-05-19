"""
Concrete class for N X N tic tac toe.
"""
import numpy as np
from combinatoric_game import TwoPlayerCombinatoricGame

class TicTacToe(TwoPlayerCombinatoricGame):
    """
    Tic tac toe in two dimensions, with an N X N board.
    A player wins when they get N in a row.
    """
    def __init__(self, N_board,
                 graph_engine='networkx',
                 keep_all_solutions=False):
        self._N_board = N_board
        super(TicTacToe, self).__init__(graph_engine=graph_engine,
                                        keep_all_solutions=keep_all_solutions)

    def _return_initial_state(self):
        initial_state_arr = self._return_initial_state_arr()
        return self._state_tuple(initial_state_arr)

    def _return_next_states(self, player, state):
        state_arr = self._state_arr(state)
        next_state_arrs = self._return_next_state_arrs(player, state_arr)
        return set(self._state_tuple(arr) for arr in next_state_arrs)

    def _get_winner(self, player, state, next_state):
        state_arr = self._state_arr(state)
        next_state_arr = self._state_arr(next_state)
        return self._get_winner_from_arr(player, state_arr, next_state_arr)

    def _return_initial_state_arr(self):
        return np.zeros((self._N_board, self._N_board)).astype(int)

    def _return_next_state_arrs(self, player, state_arr):
        num_zeros = (state_arr == 0).sum()
        next_state_arrs = [np.array(state_arr) for _ in xrange(num_zeros)]
        for arr, i, j in zip(next_state_arrs, *np.where(state_arr == 0)):
            arr[i,j] = player
        return next_state_arrs

    def _get_winner_from_arr(self, player, state_arr, next_state_arr):
        # state_arr is not used in this implementation
        # player is the only possible winner in next_state
        # First check if any row column or diagonal contains all
        # elements equal to 'player'. That would mean player wins.
        if np.any(np.all(next_state_arr == player, axis=0)):
            # player has won in one of the columns
            return player
        if np.any(np.all(next_state_arr == player, axis=1)):
            # player has won in one of the rows
            return player
        if np.all(np.diag(next_state_arr) == player):
            # player has won on the principal diagonal
            return player
        if np.all(np.diag(np.fliplr(next_state_arr)) == player):
            # player has won on the opposite diagonal
            return player

        # If we get here then there is no winner in next_state.
        # If there are no more open spaces it is a draw,
        # otherwise the game is still in play.
        if not np.any(next_state_arr == 0):
            return 0
        else:
            return None

    def _state_arr(self, state):
        """Convert tuple state into an array."""
        return np.reshape(state, (self._N_board, self._N_board))

    def _state_tuple(self, state_arr):
        """Convert state array into a tuple.  Output the
        canonical rotation of the board."""
        rotations = [np.rot90(state_arr, n) for n in xrange(4)]
        rotations.extend([arr.transpose() for arr in rotations])
        return min(tuple(np.ravel(rt)) for rt in rotations)
