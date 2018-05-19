"""
Base class for solving a two player combinatoric game.
"""
import abc
import networkx as nx
from collections import deque

class CombinatoricGame:
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph_engine='networkx', keep_all_solutions=False):
        graph_engines = {'networkx': nx.DiGraph}
        self._graph = graph_engines[graph_engine]()
        self._optimal_move_graph = graph_engines[graph_engine]()
        self._create_game_graph()
        self._find_optimal_solution(keep_all_solutions=keep_all_solutions)

    @abc.abstractmethod
    def _create_game_graph(self):
        return

    @abc.abstractmethod
    def _find_optimal_solution(self, keep_all_solutions=False):
        return

class OnePlayerCombinatoricGame(CombinatoricGame):
    __metaclass__ = abc.ABCMeta

    def _create_game_graph(self):
        # Create the game graph by breadth first search
        start = self._return_initial_state()
        queue = deque()
        queue.append(start)
        self._graph.add_node(start)

        while queue:
            state = queue.popleft()
            next_states = self._return_next_states(state)

            # Go through the next states and see which ones
            # should be appended to the queue. Also add any
            # states to the end game sets if appropriate.
            for next_state in next_states:
                if next_state in self._graph: continue
                points = self._get_final_score(state, next_state)
                if points is not None:
                    # terminal state
                    self._optimal_move_graph.add_node(next_state,
                                                      value=points)
                else:
                    queue.append(next_state)

            # Add edges from the current state to all of the next states
            for next_state in next_states:
                self._graph.add_edge(state, next_state)

    def _find_optimal_solution(self, keep_all_solutions=False):
        new_solved_nodes = set(self._optimal_move_graph.nodes())
        while new_solved_nodes:
            # Get all of the parents of the recently solved nodes
            candidate_nodes = set(pred_node for node in new_solved_nodes
                                  for pred_node in self._graph.predecessors(node)
                                  if pred_node not in self._optimal_move_graph)
            new_solved_nodes = set()
            for candidate_node in candidate_nodes:
                value, move_to_node = self._get_optimal_move(candidate_node)
                if value is not None:
                    self._optimal_move_graph.add_node(candidate_node,
                                                      value=value)
                    self._optimal_move_graph.add_edge(candidate_node,
                                                      move_to_node)
                    new_solved_nodes.add(candidate_node)

        if len(self._graph) != len(self._optimal_move_graph):
            raise NotSolvedException("Size of graph = {}, number solved = {}."\
                                         .format(len(self._graph),
                                                 len(self._optimal_move_graph)))

        if keep_all_solutions:
            # Go through all of the nodes and add all possible optimal moves
            for node in self._graph:
                for move_to_node in self._get_optimal_next_nodes(node):
                    self._optimal_move_graph.add_edge(node, move_to_node)

    def _get_optimal_move(self, node):
        """Return the value of the node, and an optimal move for the given
        node, if it's possible to compute given the state of
        self._optimal_move_graph.  If it's not possible to compute
        at this point, return (None, None)."""
        if any(succ_node not in self._optimal_move_graph
               for succ_node in self._graph.successors(node)):
            return None, None

        return max(((self._optimal_move_graph.node[succ_node]['value'], succ_node)
                    for succ_node in self._graph.successors(node)),
                   key=lambda (val, nd): val)

    def _get_optimal_next_nodes(self, node):
        """Get all possible moves that are still optimal.  Assumes that
        self._optimal_move_graph is filled out with at least one
        optimal move for each node."""
        value = self._optimal_move_graph.node[node]['value']
        return [succ_node for succ_node in self._graph.successors(node)
                if value == self._optimal_move_graph.node[succ_node]['value']]

    @abc.abstractmethod
    def _return_initial_state(self):
        """Returns the initial state of the game, from which
        the player first moves."""
        return

    @abc.abstractmethod
    def _return_next_states(self, state):
        """Return the next states that it is possible to reach in
        one move from the given state."""
        return

    @abc.abstractmethod
    def _get_final_score(self, state, next_state):
        """Returns the final score for the player if they
        move from state to next_state, and next_state is
        a terminal state.  (If next_state is not terminal,
        then None is returned.)  Note that the outpt of
        this method should *only depend on next_state*.
        The state variable is provided as a potential
        computational convenience. It is assumed that
        'state' is not a terminal state."""
        return

class TwoPlayerCombinatoricGame(CombinatoricGame):
    __metaclass__ = abc.ABCMeta

    def _create_game_graph(self):
        # Create the game graph by breadth first search
        start = (1, self._return_initial_state())
        queue = deque()
        queue.append(start)
        self._graph.add_node(start)
        
        while queue:
            player, state = queue.popleft()
            next_player = 1 if player == 2 else 2
            next_states = self._return_next_states(player, state)

            # Go through the next states and see which ones
            # should be appended to the queue.  Also add any
            # states to the end game sets if appropriate.
            for next_state in next_states:
                if (next_player, next_state) in self._graph: continue
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
        new_solved_nodes = set(self._optimal_move_graph.nodes())
        while new_solved_nodes:
            # Get all of the parents of the recently solved nodes
            candidate_nodes = set(pred_node for node in new_solved_nodes
                                  for pred_node in self._graph.predecessors(node)
                                  if pred_node not in self._optimal_move_graph)
            new_solved_nodes = set()
            for candidate_node in candidate_nodes:
                winner, move_to_node = self._get_optimal_move(candidate_node)
                if winner in {0, 1, 2}:
                    self._optimal_move_graph.add_node(candidate_node,
                                                      winner=winner)
                    self._optimal_move_graph.add_edge(candidate_node,
                                                      move_to_node)
                    new_solved_nodes.add(candidate_node)

        if len(self._graph) != len(self._optimal_move_graph):
            raise NotSolvedException("Size of graph = {}, number solved = {}."\
                                         .format(len(self._graph),
                                                 len(self._optimal_move_graph)))

        if keep_all_solutions:
            # Go through all of the nodes and add all possible optimal moves
            for node in self._graph:
                for move_to_node in self._get_optimal_next_nodes(node):
                    self._optimal_move_graph.add_edge(node, move_to_node)

    def _get_optimal_move(self, node):
        """Return the winner (None, 0, 1, or 2, with similar meaning to
        the return value of _get_winner), and an optimal move for the
        given node if it's possible to compute given the state of
        self._optimal_move_graph.  If it's not possible to compute
        at this point, return (None, None)."""
        player, _ = node
        other_player = 1 if player == 2 else 2
        best_move = {}
        unlabeled_successors = False
        for succ_node in self._graph.successors(node):
            if succ_node in self._optimal_move_graph:
                winner = self._optimal_move_graph.node[succ_node]['winner']
                if winner == player:
                    # player can win, should move here
                    return winner, succ_node
                elif winner == 0:
                    # draw
                    best_move['winner'] = winner
                    best_move['move_to_node'] = succ_node
                else:
                    # other player would win if you move here
                    if best_move.get('winner', other_player) == other_player:
                        best_move['winner'] = winner
                        best_move['move_to_node'] = succ_node
            else:
                unlabeled_successors = True

        if unlabeled_successors:
            return None, None
        else:
            return best_move['winner'], best_move['move_to_node']

    def _get_optimal_next_nodes(self, node):
        """Get all possible moves that are still optimal.  Assumes that
        self._optimal_move_graph is filled out with at least one
        optimal move for each node."""
        winner = self._optimal_move_graph.node[node]['winner']
        return [succ_node for succ_node in self._graph.successors(node)
                if winner == \
                    self._optimal_move_graph.node[succ_node]['winner']]

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
    def _get_winner(self, player, state, next_state):
        """Returns which player wins, if any, if the given player
        moves so that the game goes from state to next_state.
        Note that the output of this method should *only depend
        on next_state, and possibly player, but not state*.
        The state variable is provided as a potential
        computational convenience. (It is okay for the output
        to depend on player, since this would be the same
        for any node with a link into next_state.)
        It is assumed that at 'state' the game is still in
        play (i.e. no winner at that state and it's not
        a draw).
        
        Specifically, should return:
        None if the game is still in play at next_state
        0 if the game is a draw at next_state
        1 if player one wins at next_state
        2 if player two wins at next_state"""
        return


class NotSolvedException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
