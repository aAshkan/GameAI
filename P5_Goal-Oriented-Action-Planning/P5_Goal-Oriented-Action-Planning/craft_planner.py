import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappush, heappop
from math import ceil

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Returns a function to determine whether a state meets a rule's requirements.
    # This code runs once, when the rules are constructed before the search is attempted.
    consumes = []
    requires = []

    if ('Consumes' in rule.keys()):
      consumes = [(item, rule['Consumes'][item]) for item in rule['Consumes']]
      #print("Consumes: ", consumes)

    if ('Requires' in rule.keys()):
        requires = [item for item in rule['Requires'].items()] #.keys
        #print("Requires: ", requires)

    #produce = [(item, rule['Produces'][item]) for item in rule['Produces']]
    #print("Produces: ", produce)
    

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        #return True

        for item, number in consumes:
            #if (name == 
            #print(state[name])
            if item not in state:
                return False
            elif (state[item] < number):
                return False

        for item in requires:
            if item not in state.items():
                return False

        return True

    return check


def make_effector(rule):
    # Returns a function which transitions from state to new_state given the rule.
    # This code runs once, when the rules are constructed before the search is attempted.
    consumes = []
    produce = []

    if ('Consumes' in rule.keys()):
      consumes = [(item, rule['Consumes'][item]) for item in rule['Consumes']]

    if ('Produces' in rule.keys()):
        produce = [(item, rule['Produces'][item]) for item in rule['Produces']]
        #print (produce)

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].


        next_state = None
        next_state = state.copy()

        for item, number in consumes:
            next_state[item] -= number

        for item, number in produce:
            if item not in state:       #doesn't exist
                next_state[item] = 0
            next_state[item] += number
        return next_state

    return effect


def make_goal_checker(goal):
    # Returns a function which checks if the state has met the goal criteria.
    # This code runs once, before the search is attempted.


    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for item, number in goal.items():
            if item not in state:
                return False
            elif (state[item] < number):
                return False

        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def make_heuristic(goal):
    # Maximum needed for objects
    maxCart = 0
    maxRail = 0
    # Maximum needed for resources
    maxCoal = 0
    maxCobble = 0
    maxOre = 0
    maxWood = 0
    # Maximum needed for materials
    maxIngot = 0
    maxPlank = 0
    maxStick = 0

    # Tool flags
    needBench = False
    needFurnace = False

    # Calculate maximums
    # Tools
    if 'bench' in goal:
        needBench = True
    if 'furnace' in goal:
        needFurnace = True
        needBench = True
    if 'wooden_pickaxe' in goal:
        maxPlank += 3
        maxStick += 2
        needBench = True
    if 'stone_pickaxe' in goal:
        maxCobble += 3
        maxStick += 2
        needBench = True
    if 'iron_pickaxe' in goal:
        maxIngot += 3
        maxStick += 2
        needBench = True
        needFurnace = True
    # Goods
    if 'cart' in goal:
        maxIngot += 5*goal['cart']
        maxCart += goal['cart']
        needBench = True
        needFurnace = True
    if 'rail' in goal:
        railVal = goal['rail']+16
        while railVal > 0:
            railVal -= 16
            maxIngot += 6
            maxStick += 1
        maxRail += goal['rail']+16
        needBench = True
        needFurnace = True
    # Crafted Resources
    if 'ingot' in goal:
        maxIngot += goal['ingot']
        needFurnace = True
    if 'plank' in goal:
        maxPlank += goal['plank']
    if 'stick' in goal:
        maxStick += goal['stick']
    # Farmed Resources
    if 'coal' in goal:
        maxCoal += goal['coal']
    if 'cobble' in goal:
        maxCobble += goal['cobble']
    if 'ore' in goal:
        maxOre += goal['ore']
    if 'wood' in goal:
        maxWood += goal['wood']

    if needBench:
        maxPlank += 4
    if needFurnace:
        maxCobble += 8

    maxCoal += maxIngot
    maxOre += maxIngot

    # Need stone pickaxe
    if maxOre > 0 or maxCoal > 0:
        maxStick += 2
        maxCobble += 3

    # Calculate necessary resources
    stickNum = maxStick
    while stickNum > 0:
        stickNum -= 4
        maxPlank += 2

    plankNum = maxPlank
    while plankNum > 0:
        plankNum -= 4
        maxWood += 1

    #print("ingotMax", maxIngot)
    #print("oreMax", maxOre)
    #print("coalMax", maxCoal)
    #print("stickMax", maxStick)
    #print("plankMax", maxPlank)
    #print("woodMax", maxWood)
    #print("cartMax", maxCart)
    #print("railMax", maxRail)
    #print("cobbleMax", maxCobble)

    def heuristic(state):

        # Ignore moves which create duplicates of tools
        if state['wooden_pickaxe'] > 1 or state['wooden_axe'] > 1 or \
        state['stone_pickaxe'] > 1 or state['stone_axe'] > 1 or \
        state['iron_pickaxe'] > 1 or state['iron_axe'] > 1 or \
        state['bench'] > 1 or state['furnace'] > 1:
            return float('-inf')
        # Ignore moves which generate more resources than necessary
        elif state['ingot'] > maxIngot or state['plank'] > maxPlank+4 or state['stick'] > maxStick+4:
            return float('-inf')
        elif state['cart'] > maxCart or state['rail'] > maxRail:
            return float('-inf')
        elif state['coal'] > maxCoal or state['cobble'] > maxCobble or state['ore'] > maxOre or state['wood'] > maxWood:
            return float('-inf')

        resourceVal = 0
        if maxIngot > 0:
            resourceVal += state['ingot']/maxIngot
        if maxPlank > 0:
            resourceVal += state['plank']/maxPlank
        if maxStick > 0:
            resourceVal += state['stick']/maxStick

        farmVal = 0
        if maxCoal > 0:
            farmVal += state['coal']/maxCoal
        elif maxCobble > 0:
            farmVal += state['cobble']/maxCobble
        elif maxOre > 0:
            farmVal += state['ore']/maxOre
        elif maxWood > 0:
            farmVal += state['wood']/maxWood

        objectVal = 0
        if maxCart > 0:
            objectVal += state['cart']/maxCart
        elif maxRail > 0:
            objectVal += state['rail']/maxRail

        return resourceVal*10 + objectVal*100 + farmVal*10
    return heuristic


def search(graph, state, is_goal, limit, heuristic):
    start_time = time()
    pre = {}
    currCost = {}

    pre[state] = None
    currCost[state] = 0
    q = []
    heappush (q, (currCost[state] + 0, currCost[state], None, state))
    # Search
    counter = 0

    while time() - start_time < limit:
        # Get node with best heuristic
        q.sort()
        q.reverse()
        node = heappop(q)
        h, c, a, n = node
        #print(h)
        if is_goal(n):
            print("Goal has been found")
            print("Time it took:", time() - start_time)
            break

        for a2, n2, c2 in graph(n):
            newCost = currCost[n] + c2
            if n2 not in currCost or newCost < currCost[n2]:
                currCost[n2] = newCost
                pre[n2] = n
                heurVal = heuristic(n2)
                heappush (q, (currCost[n2] + heurVal, currCost[n2], a2, n2))



    if is_goal(n):
        path = []
        final_cost = currCost[n]

        while n:
            path.append(n)
            n = pre[n]
        path.reverse()
        return final_cost, time()-start_time, currCost, path
    else:
        # Failed to find a path
        print("Failed to find a path from", state, 'within time limit.')
        return None, None



if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # List of items that can be in your inventory:
    print('All items:',Crafting['Items'])

    # List of items in your initial inventory with amounts:
    print('Initial inventory:',Crafting['Initial'])

    # List of items needed to be in your inventory at the end of the plan:
    print('Goal:',Crafting['Goal'])

    # Dict of crafting recipes (each is a dict):
    print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    heuristic = make_heuristic(Crafting['Goal'])

    final_cost, computationTime, nodeCosts, path = search(graph, state, is_goal, 45, heuristic)
    print("Stop here")
    if path:
        for i in path:
            print (i)
        print("The program found it's goal in", computationTime, "seconds.")
        print("The in-game time cost is", final_cost, "seconds.")
        print("The number of states explored is", len(nodeCosts), ".")
    # Search - This is you!