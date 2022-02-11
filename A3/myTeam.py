# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random
from game import Directions, Actions
from math import exp

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='StandardAgent', second='StandardAgent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

##################################
#           My Team              #
##################################
        
class StandardAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.weights = [30.0, 1.0, -175.0, 0.8, 20.0, 0.5, -5, 0.5, 40.0, 0.8, 100.0, 0.3,
                      0.0, 0.01, 0.0, 0.8, 500.0, 0.8, -1.0, 0.5, 0.0, 0.0001, 0.8]
           
    def chooseAction(self, gameState):
        actions = [a for a in gameState.getLegalActions(self.index) if a != Directions.STOP]
        
        previousPos = gameState.getAgentState(self.index).getPosition()
        possibleCells = [self.getActionCoordinates(action, previousPos) for action in actions]

        foodGrid = self.getFood(gameState)
        foodList = foodGrid.asList()
        capsules = self.getCapsules(gameState)
        wallsGrid = gameState.getWalls()
        
        defenseFoodGrid = self.getFoodYouAreDefending(gameState)
        defenseFoodList = defenseFoodGrid.asList()
        defenseCapsules = self.getCapsulesYouAreDefending(gameState)
      
        allies = [gameState.getAgentState(i) for i in self.getTeam(gameState)]
        hunters = [a for a in allies if a.isPacman and a.getPosition() != None]
        defenders = [a for a in allies if not a.isPacman and a.getPosition() != None]
        
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      
        isPacman = gameState.getAgentState(self.index).isPacman
        amScared = gameState.getAgentState(self.index).scaredTimer != 0
        
        defendMode = False
        
        if invaders:
            minDistance = 999999
            closestAllied = None
            for index in self.getTeam(gameState):
                minInvaderDistance = min([self.getMazeDistance(gameState.getAgentState(index).getPosition(), i.getPosition()) for i in invaders])
                if minInvaderDistance < minDistance:
                    minDistance = minInvaderDistance
                    closestAllied = index
            if closestAllied == self.index:
                defendMode = True  
        
        if not defendMode:
            evalFunc = self.generateEvalFunc(self.offensiveFeatures(wallsGrid, foodList, foodGrid, capsules, hunters, ghosts, defenders, possibleCells, previousPos, isPacman))
        else:
            for cell in possibleCells:
                if cell in foodList:
                    return [a for a, c in zip(actions, possibleCells) if c == cell][0]
            evalFunc = self.generateEvalFunc(self.defensiveFeatures(amScared, defenseFoodList, defenseCapsules, defenders, invaders, ghosts, possibleCells))
        
        actionPoints = [evalFunc(cell) for cell in possibleCells]
        if not actionPoints:
            return Directions.STOP
        maxValue = max(actionPoints)
        bestActions = [a for a, v in zip(actions, actionPoints) if v == maxValue]
        return random.choice(bestActions)

    def offensiveFeatures(self, wallsGrid, foodList, foodGrid, capsules, hunters, ghosts, defenders, possibleCells, previousPos, isPacman):
        features = []
      
        for food in foodList:
            features.append(self.featureItem(self.weights[0], self.weights[1], food[0], food[1]))
            
            isLonely = True
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    isCellInGrid = (food[0] + i < foodGrid.width) and (food[0] + i >= 0) and (food[1] + j < foodGrid.height) and (food[1] + j) >= 0
                    if (i != 0 or j != 0) and isCellInGrid and foodGrid[food[0] + i][food[1] + j]:
                        isLonely = False
                        break
            
            if isLonely:
                features.append(self.featureItem(self.weights[10], self.weights[11], food[0], food[1]))                            
            
        for capsule in capsules:
            features.append(self.featureItem(self.weights[8], self.weights[9], capsule[0], capsule[1]))
      
        for ghost in ghosts:
            if ghost.scaredTimer == 0:
                if isPacman or self.getMazeDistance(ghost.getPosition(), previousPos) < 8:
                    ghostFeature = self.featureItem(self.weights[2], self.weights[3], ghost.getPosition()[0], ghost.getPosition()[1])
                    features.append(ghostFeature)
                    features.append(self.calculateWallPenalty(wallsGrid, ghostFeature))
            else:
                features.append(self.featureItem(self.weights[4], self.weights[5], ghost.getPosition()[0], ghost.getPosition()[1]))
                
        for hunter in hunters:
            if len(possibleCells) > 2:
                features.append(self.featureItem(self.weights[6], self.weights[7], hunter.getPosition()[0], hunter.getPosition()[1]))
    
        for defender in defenders:
            if len(possibleCells) > 2:
                features.append(self.featureItem(self.weights[18], self.weights[19], defender.getPosition()[0], defender.getPosition()[1]))
            
        return features
    
    def calculateWallPenalty(self, wallsGrid, ghostFeature):
        def getWallPenaltyForCell(x, y):
            numberOfWalls = 0
            for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    isCellInGrid = x + i < wallsGrid.width and x + i >= 0 and y + j < wallsGrid.height and y + j >= 0
                    if isCellInGrid and wallsGrid[int(x + i)][int(y + j)]:
                        numberOfWalls += 1
            
            return numberOfWalls * ghostFeature(x, y) * self.weights[22]
            
        return getWallPenaltyForCell
    
    def defensiveFeatures(self, amScared, defenseFoodList, defenseCapsules, defenders, invaders, ghosts, possibleCells):
        features = []
      
        for food in defenseFoodList:
            features.append(self.featureItem(self.weights[12], self.weights[13], food[0], food[1]))         
            
        for capsule in defenseCapsules:
            features.append(self.featureItem(self.weights[20], self.weights[21], capsule[0], capsule[1]))
      
        for invader in invaders:
             if amScared:
                features.append(self.featureItem(self.weights[14], self.weights[15], invader.getPosition()[0], invader.getPosition()[1]))
             else:
                features.append(self.featureItem(self.weights[16], self.weights[17], invader.getPosition()[0], invader.getPosition()[1]))
                
        for defender in defenders:
            if len(possibleCells) > 2:
                features.append(self.featureItem(self.weights[18], self.weights[19], defender.getPosition()[0], defender.getPosition()[1]))
              
        return features
    
    def getActionCoordinates(self, action, previousCoordinates):
        dx, dy = Actions.directionToVector(action)
        return (previousCoordinates[0] + dx, previousCoordinates[1] + dy)
    
    def generateEvalFunc(self, features):
        def evalC(coordinate):
            return utilityValue(coordinate[0], coordinate[1], features)
        return evalC
      
    def featureItem(self, A, sigma, x0, y0):
        def gaussianKernel(x, y):
            distance = self.getMazeDistance((x, y), (x0, y0))
            return A * exp(-(distance) / (2.0 * sigma * sigma))
        return gaussianKernel
    
    def setWeight(self, Weight):
        self.weights = Weight

def featureValue(x, y, g):
    return g(x, y)

def utilityValue(x, y, features):
    return sum([featureValue(x, y, feature) for feature in features])