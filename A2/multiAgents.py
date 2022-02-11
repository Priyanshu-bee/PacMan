# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        distance = 0
        avgGhostDistance = 0
        minGhostDistance = float('inf')
        minFoodDistance = float('inf')
        Food = newFood.asList()
        noShit = 0
        numWalls = 0
        minFoodPos = [0,0]
        count = 0
        if manhattanDistance(newPos,currentGameState.getPacmanPosition())==0: noShit = -10
        for i in Food:
            mFD = manhattanDistance(newPos,i)
            if mFD<minFoodDistance:
                minFoodDistance = mFD
                minFoodPos = i
        for i in range(currentGameState.getNumAgents()): 
            if not i==0 and minGhostDistance>2:
                if sum(newScaredTimes)==0 or not newScaredTimes[i-1]==0:
                    count = count+1
                    mD = manhattanDistance(newPos,currentGameState.getGhostPosition(i))
                    minGhostDistance = min(minGhostDistance, mD)
                    avgGhostDistance = avgGhostDistance+mD
        avgGhostDistance = avgGhostDistance/count
        if minGhostDistance<=4: 
            if avgGhostDistance>=5: distance = 1000*(5-minGhostDistance) 
            else: distance = 1500-3*minGhostDistance
        if oldFood.count()-newFood.count()==1:
            if minFoodDistance>=3: minFoodDistance = 1
        elif minGhostDistance>4 :
            if minFoodPos[0]-newPos[0]<0 and successorGameState.hasWall(newPos[0]-1,newPos[1]): 
                numWalls = numWalls+1
            if minFoodPos[0]-newPos[0]>0 and successorGameState.hasWall(newPos[0]+1,newPos[1]): 
                numWalls = numWalls+1
            if minFoodPos[1]-newPos[1]<0 and successorGameState.hasWall(newPos[0],newPos[1]-1): 
                numWalls = numWalls+1
            if minFoodPos[1]-newPos[1]>0 and successorGameState.hasWall(newPos[0],newPos[1]+1): 
                numWalls = numWalls+1
        if not sum(newScaredTimes)==0: 
            if 0 in newScaredTimes: distance = -4*minGhostDistance
            else: distance = 4*(minGhostDistance-avgGhostDistance)
        if minGhostDistance<=2: return -1*(3-minGhostDistance)*10000
        if numWalls>2: numWalls = 0
        else: numWalls = 2
        return successorGameState.getScore()-4*minFoodDistance-distance+noShit+numWalls

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        return gameState.getLegalActions(0)[self.maxAgent(gameState, 1)]

    def maxAgent(self, gameState, level):
        all_moves = gameState.getLegalActions(0)
        val = float('-inf')
        out = 0
        for j in range(len(all_moves)):
            state = gameState.generateSuccessor(0, all_moves[j])
            if state.isWin(): count = self.evaluationFunction(state)
            elif state.isLose(): count = self.evaluationFunction(state)
            else: count = self.minAgent(state, 1, level)
            if level==1 and count>val: out = j
            val = max(val, count)
        if level==1: return out
        return val


    def minAgent(self, gameState, Agent, level):
        all_moves = gameState.getLegalActions(Agent)
        val = float('inf')
        for j in range(len(all_moves)):
            state = gameState.generateSuccessor(Agent, all_moves[j])
            if state.isWin(): val = min(val, self.evaluationFunction(state))
            elif state.isLose(): val = min(val, self.evaluationFunction(state))
            else:
                if Agent<state.getNumAgents()-1:
                    val = min(val, self.minAgent(state, Agent+1, level))
                else:
                    if self.depth==level:
                        val = min(val, self.evaluationFunction(state))
                    else:
                        val = min(val, self.maxAgent(state, level+1)) 
        return val

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        return gameState.getLegalActions(0)[self.maxAgent(gameState, 1, float('-inf'), float('inf'))]

    def maxAgent(self, gameState, level, alpha, beta):
        all_moves = gameState.getLegalActions(0)
        val = float('-inf')
        out = 0
        for j in range(len(all_moves)):
            state = gameState.generateSuccessor(0, all_moves[j])
            if state.isWin(): count = self.evaluationFunction(state)
            elif state.isLose(): count = self.evaluationFunction(state)
            else: count = self.minAgent(state, 1, level, alpha, beta)
            if level==1 and count>val: out = j
            val = max(val, count)
            alpha = max(alpha, val)
            if val>beta and not level==1: break
        if level==1: return out
        return val


    def minAgent(self, gameState, Agent, level, alpha, beta):
        all_moves = gameState.getLegalActions(Agent)
        val = float('inf')
        for j in range(len(all_moves)):
            state = gameState.generateSuccessor(Agent, all_moves[j])
            if state.isWin(): val = min(val, self.evaluationFunction(state))
            elif state.isLose(): val = min(val, self.evaluationFunction(state))
            else:
                if Agent<state.getNumAgents()-1:
                    val = min(val, self.minAgent(state, Agent+1, level, alpha, beta))
                else:
                    if self.depth==level:
                        val = min(val, self.evaluationFunction(state))
                    else:
                        val = min(val, self.maxAgent(state, level+1, alpha, beta))
            beta = min(beta, val)
            if val<alpha: break
        return val

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        return gameState.getLegalActions(0)[self.maxAgent(gameState, 1)]

    def maxAgent(self, gameState, level):
        all_moves = gameState.getLegalActions(0)
        val = float('-inf')
        out = 0
        for j in range(len(all_moves)):
            state = gameState.generateSuccessor(0, all_moves[j])
            if state.isWin(): count = self.evaluationFunction(state)
            elif state.isLose(): count = self.evaluationFunction(state)
            else: count = self.minAgent(state, 1, level)
            if level==1 and count>val: out = j
            val = max(val, count)
        if level==1: return out
        return val


    def minAgent(self, gameState, Agent, level):
        all_moves = gameState.getLegalActions(Agent)
        val = 0
        for j in range(len(all_moves)):
            state = gameState.generateSuccessor(Agent, all_moves[j])
            if state.isWin(): val = val+self.evaluationFunction(state)
            elif state.isLose(): val = val+self.evaluationFunction(state)
            else:
                if Agent<state.getNumAgents()-1:
                    val = val+self.minAgent(state, Agent+1, level)
                else:
                    if self.depth==level:
                        val = val+self.evaluationFunction(state)
                    else:
                        val = val+self.maxAgent(state, level+1)
        return val/len(all_moves)

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>

    Used values of distance from nearest food item, average distance from ghosts, 
    distance from nearest ghost, number of walls between nearest food item and pacman,
    total number of food items and scaredTimer for ghosts to return a suitable Score for different states"""

    "*** YOUR CODE HERE ***"
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    distance = 0
    count = 0
    avgGhostDistance = 0
    minGhostDistance = float('inf')
    minFoodDistance = float('inf')
    Food = newFood.asList()
    numWalls = 0
    minFoodPos = [0,0]
    for i in Food:
        mFD = manhattanDistance(newPos,i)
        if mFD<minFoodDistance:
            minFoodDistance = mFD
            minFoodPos = i
    for i in range(currentGameState.getNumAgents()): 
        if not i==0 and minGhostDistance>2:
            if sum(newScaredTimes)==0 or not newScaredTimes[i-1]==0:
                count = count+1
                mD = manhattanDistance(newPos,currentGameState.getGhostPosition(i))
                minGhostDistance = min(minGhostDistance, mD)
                avgGhostDistance = avgGhostDistance+mD
    avgGhostDistance = avgGhostDistance/count
    if minGhostDistance<=4: 
        if avgGhostDistance>=5: distance = 1000*(5-minGhostDistance) 
        else: distance = 1500-3*minGhostDistance
    if minGhostDistance>4 :
        if minFoodPos[0]-newPos[0]<0 and currentGameState.hasWall(newPos[0]-1,newPos[1]): 
            numWalls = numWalls+1
        if minFoodPos[0]-newPos[0]>0 and currentGameState.hasWall(newPos[0]+1,newPos[1]): 
            numWalls = numWalls+1
        if minFoodPos[1]-newPos[1]<0 and currentGameState.hasWall(newPos[0],newPos[1]-1): 
            numWalls = numWalls+1
        if minFoodPos[1]-newPos[1]>0 and currentGameState.hasWall(newPos[0],newPos[1]+1): 
            numWalls = numWalls+1
    if not sum(newScaredTimes)==0: 
        if 0 in newScaredTimes: distance = -4*minGhostDistance
        else: distance = 4*(minGhostDistance-avgGhostDistance)
    if minGhostDistance<=2: return -1*(3-minGhostDistance)*10000
    if numWalls>2: numWalls = 0
    elif not numWalls==0: numWalls = 1
    else: numWalls = 2
    if newFood.count()==0: minFoodDistance=0
    return currentGameState.getScore()-2*minFoodDistance-10*newFood.count()-distance+numWalls

# Abbreviation
better = betterEvaluationFunction
