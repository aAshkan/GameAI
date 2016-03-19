
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log
import math
num_nodes = 100
explore_faction = 2.

def traverse_nodes(node, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    """
    while not state.is_terminal():
        if node.untried_actions != []:
            return expand_leaf(node, state)
        else:
            max_score = 0.0
            UCB = 0.0
            best_node = None
            print (list(node.child_nodes.values()))
            for child in list(node.child_nodes.values()):
                if identity is "red":   #need to change it for general situation
                    UCB = child.wins/child.visits + explore_faction*sqrt(2.0*log(child.parent.visits)/child.visits)
                elif identity is "blue":
                    UCB = (1-child.wins/child.visits) + explore_faction*sqrt(2.0*log(child.parent.visits)/child.visits)
                if UCB > max_score:
                    best_node = child
                    max_score = UCB
            node = best_node
            state.apply_move(node.parent_action)
    return node
    """
    while not state.is_terminal():
        if node.untried_actions:
            return expand_leaf(node, state)
        else:
            valueList = list(node.child_nodes.values())
            if identity == state.player_turn: 
                node = max(valueList, key = lambda c: c.wins/c.visits + explore_faction*sqrt(2*log(c.parent.visits)/c.visits))
            else:
                #node = max(valueList, key = lambda c:  min((c.wins/c.visits)) + (explore_faction*sqrt(2*log(c.parent.visits)/c.visits)))
                node = max(valueList, key = lambda c: 1 - (c.wins/c.visits) + (explore_faction * sqrt(2*log(c.parent.visits)/c.visits)))
            state.apply_move(node.parent_action)
    return node

    #pass
    # Hint: return leaf_node


def expand_leaf(node, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        state:  The state of the game.

        Returns:    The added child node.

    """
    m = choice (node.untried_actions)
    state.apply_move(m)
    new_node = MCTSNode (parent = node, parent_action = m , action_list = state.legal_moves) #needs fixing
    node.untried_actions.remove(m)
    node.child_nodes[m] = new_node
    return new_node

    #pass
    # Hint: return new_node


def rollout(state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        state:  The state of the game.

    """
    while not state.is_terminal():
        #print ("asd")
        state.apply_move(choice(state.legal_moves))
    #pass


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    #walker_node = node
    #while  walker_node:
    while node:
        node.wins += won
        node.visits += 1
        node = node.parent
    #pass


def think(state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = state.player_turn
    root_node = MCTSNode(parent=None, parent_action=None, action_list=state.legal_moves)

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state.copy()

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        #if node.untried_actions:
        #node = expand_leaf(node,sampled_game)
        node = traverse_nodes(node,sampled_game,identity_of_bot)
        rollout(sampled_game)

        if sampled_game.winner == identity_of_bot:
            won = 1
        elif sampled_game.winner == "tie":
            won = 0
        else:
            won = -1

        backpropagate(node,won)


    # Return an action, typically the most frequently used action (from the root) or the action with the best
    
    max_score = 0.0
    best_move = None
    best_node = node
 

    listValue = list(root_node.child_nodes.values())
    #best_node
    
    """
    print(list(root_node.child_nodes.values()))

    for child in list(root_node.child_nodes.values()):
        best_choice = child.wins/child.visits
        if best_choice > max_score:
            max_score = best_choice
            best_move = child.parent_action
    

                #state.apply_move(best_node.parent_action)
    #state.apply_move(best_node.parent_action)

    # estimated win rate.'
    #print(best_move)

    return best_move
    """   
    best_node = max(listValue, key = lambda c: c.wins/c.visits)

    return best_node.parent_action
