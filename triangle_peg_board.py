"""
Triangle peg board game.
"""
import numpy as np
from combinatoric_game import OnePlayerCombinatoricGame

class TrianglePegBoard(OnePlayerCombinatoricGame):
    """
    Triangle peg board game, where the longest side
    has N pegs.  The rows form an equilateral triangle,
    and each row has 1, 2, 3, ..., N pegs in it. The
    top of the triangle (first row) starts of empty
    and the remaining spaces are filled with pegs.
    On each move, one peg can jump another in a line
    to remove the peg.  The goal is to minimize the
    number of pegs remaining at the end when no more
    moves are possible.
    """
    def __init__(self, N_base,
                 graph_engine='networkx',
                 keep_all_solutions=False):
        self._N_base = N_base
        super(TrianglePegBoard, self).__init__(graph_engine=graph_engine,
                                               keep_all_solutions=keep_all_solutions)

    def _return_initial_state(self):
        return (0,) + (1,)*self._N_base*(self._N_base+1)/2

    def _return_next_states(self, state):
        return set(self._state_tuple(state_list)
                   for state_list in self._iter_next_state_lists(state))

    def _get_final_score(self, _, state):
        if any(True for _ in self._iter_next_state_lists(state)):
            return None
        return -sum(state)

    def _iter_next_state_lists(self, state):
        state_list = self._state_list(state)
        for rot_state_list in self._all_rotation_lists(state_list):
            for idx, row in enumerate(rot_state_list[2:], 2):
                for new_row in self._row_moves(row):
                    yield rot_state_list[:idx] + [new_row] + rot_state_list[idx+1:]

    def _state_list(self, state):
        """Convert tuple state into a list of lists."""
        state_list = []
        idx = 0
        for row_size in xrange(1, self._N_base+1):
            state_list.append(list(state[idx:idx+row_size]))
            idx += row_size
        return state_list
                    
    def _state_tuple(self, state_list):
        """Convert state list into a tuple.  Output the
        canonical rotation/reflection of the board."""
        return min(tuple(sum(transf_state_list, [])) for transf_state_list
                   in self._all_transformation_lists(state_list))

    def _all_rotation_lists(self, state_list):
        """Return the state lists that represent all rotations of
        the board, (including 0 degrees)."""
        # 0 degree rotation
        yield [list(x) for x in state_list]
        # 120 degree rotation
        yield [[row[idx] for row in state_list if len(row) > idx]
               for idx in xrange(self._N_base-1, -1, -1)]
        # 240 degree rotation
        yield [[row[-idx] for row in reversed(state_list) if len(row) >= idx]
               for idx in xrange(self._N_base, 0, -1)]

    def _all_transformation_lists(self, state_list):
        """Return the state lists that represent all symmetry
        transformations of the board, (rotations and reflections)."""
        for rot_state_list in self._all_rotation_lists(state_lists):
            yield rot_state_list
            yield [list(reversed(x)) for x in rot_state_list]

    def _row_moves(self, row):
        """Return all possible new configurations of the given
        row after a move is made within the line of the row."""
        for idx in xrange(len(row)-2):
            candidate = row[idx:idx+3]
            if candidate == [1,1,0]:
                yield row[:idx] + [0,0,1] + row[idx+3:]
            elif candidate == [0,1,1]:
                yield row[:idx] + [1,0,0] + row[idx+3:]
