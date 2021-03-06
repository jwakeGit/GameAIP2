
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    if len(node.untried_actions) > 0:
        if node.visits == 0:
            return (node, state)
        else:
            select_first = 1
            returner_node = node
            for move in node.untried_actions:
                #print(f'debug: move = {move}')
                node.untried_actions.remove(move)
                new_state = board.next_state(state, move)
                if select_first:
                    returner_node = expand_leaf(node, board, new_state)
                    returner_node.parent_action = move
                    node.child_nodes[move] = returner_node
                else:
                    unreturner_node = expand_leaf(node, board, new_state)
                    unreturner_node.parent_action = move
                    node.child_nodes[move] = unreturner_node
                select_first = 0
            #print(f'debug: returner action: {returner_node.parent_action}')
            return (returner_node, board.next_state(state, returner_node.parent_action))
    else:
        best_node = node
        for child in node.child_nodes.values():
            #if UCT of child > UCT of best_node:
            if(identity == board.current_player(board.next_state(state, child.parent_action))):
                if(child.visits > 0): child_UCT = (child.wins/child.visits) + (explore_faction*(sqrt(log(node.visits)/child.visits)))
                else: child_UCT = float('inf')
                if(best_node.visits > 0): best_UCT = (best_node.wins/best_node.visits) + (explore_faction*(sqrt(log(node.visits)/best_node.visits)))
                else: best_UCT = float('inf')
            else:
                if(child.visits > 0): child_UCT = (1-(child.wins/child.visits)) + (explore_faction*(sqrt(log(node.visits)/child.visits)))
                else: child_UCT = float('inf')
                if(best_node.visits > 0): best_UCT = (1-(best_node.wins/best_node.visits)) + (explore_faction*(sqrt(log(node.visits)/best_node.visits)))
                else: best_UCT = float('inf')
            if child_UCT > best_UCT:
                best_node = child
        if best_node != node: 
            new_state = board.next_state(state, best_node.parent_action)
            return traverse_nodes(best_node, board, new_state, identity)
        else: return (node, state)


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    new_node = MCTSNode()
    new_node.parent = node
    new_node.untried_actions = board.legal_actions(state)
    return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    if board.is_ended(state):
        return board.points_values(state)
    else:
        move = choice(board.legal_actions(state))
        return rollout(board, board.next_state(state, move))


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    node.wins += won
    node.visits += 1
    if node.parent:
        backpropagate(node.parent, won)


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
    
    moves = board.legal_actions(state)
    best_move = moves[0]
    best_expectation = float('-inf')

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        current_node, current_state = traverse_nodes(node, board, sampled_game, identity_of_bot)
        win_dict = rollout(board, current_state)
        if win_dict[identity_of_bot] == 1:
            backpropagate(current_node, 1)
        else:
            backpropagate(current_node, 0)

    #Set best options
    for child in root_node.child_nodes.values():
        if child.visits > 0 and (child.wins/child.visits) + (explore_faction*(sqrt(log(node.visits)/child.visits))) > best_expectation:
            best_expectation = (child.wins/child.visits) + (explore_faction*(sqrt(log(node.visits)/child.visits)))
            best_move = child.parent_action

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return best_move
