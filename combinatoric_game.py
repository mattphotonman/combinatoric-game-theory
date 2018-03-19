"""
Base class for solving a two player combinatoric game.
"""
import abc
import networkx as nx
from collections import deque

class CombinatoricGame:
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph_engine='networkx', keep_all_solutions=False):
        graph_engines = {'networkx': NetworkxGraph}
        self._graph = graph_engines[graph_engine]()
        self._optimal_move_graph = graph_engines[graph_engine]()
        self._create_game_graph()
        self._find_optimal_solution(keep_all_solutions=False)

    def _create_game_graph(self):
        # Create the game graph by breadth first search
        start = (1, self._return_initial_state())
        queue = deque()
        queue.apppend(start)
        self._graph.add_node(start)
        
        while queue:
            player, state = queue.popleft()
            next_player = 1 if player == 2 else 2
            next_states = self._return_next_states(player, state)

            # Go through the next states and see which ones
            # should be appended to the queue.  Also add any
            # states to the end game sets if appropriate.
            for next_state in next_states:
                if next_state in self._graph: continue
                winner = self._get_winner(player, state, next_state)
                if winner in {0, 1, 2}:
                    self._optimal_move_graph.add_node((next_player, next_state),
                                                      winner=winner)
                else:
                    queue.append((next_player, next_state))

            # Add edges from the current state to all of the next states
            for next_state in next_states:
                self._graph.add_edge((player, state), (next_player, next_state))

    def _find_optimal_solution(self, keep_all_solutions=False):
        solved_nodes = set(self._optimal_move_graph.nodes())
        while solved_nodes:
            for node in solved_nodes:
                # editing here

    @abc.abstractmethod
    def _return_initial_state(self):
        """Returns the initial state of the game, from which
        player 1 first moves."""
        return

    @abc.abstractmethod
    def _return_next_states(self, player, state):
        """Return the next states that it is possible to reach in
        one move by the given player starting at the given state."""
        return

    @abc.abstractmethod
    def _get_winner(player, state, next_state):
        """Returns which player wins, if any, if the given player
        moves so that the game goes from state to next_state.
        
        Specifically, should return:
        None if the game is still in play at next_state
        0 if the game is a draw at next_state
        1 if player one wins at next_state
        2 if player two wins at next_state"""
        return
