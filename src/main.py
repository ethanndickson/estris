# Tetris - Ethan Dickson Major Work 2018 - Final - Python 3.7.0b1
# Pygame 1.9.4
import pygame
import random
import csv
pygame.init()

# Pygame Requisites
pygame.display.set_caption('Tetris By Ethan Dickson')
screen_width = 405
screen_height = 700
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()

# Variables that need to be kept track of globally
dropTicker = 0 # Counter of the frequency of automatic block drops.
running = True # Pygame rendering condition

# Different Game States
playingGame = False # Condition for whether a game is currently in play
mainMenu = True # Condition for whether the main menu is being shown
InstructionsScreen = False # Same as above but for instructions
gameOver = False # ""
HighScoreScreen = False # ""
scoreSaved = False # Whether or not the current score has been saved

# Per game settings
userNameInput = []
score = 0 # The player's score
lines = 0
difficultyTimer = 400

# Constant/Configurable variables used
GridHeight = 24
GridWidth = 10
GridTopleft_x = 21
GridTopleft_y = 70
MenuBackground = (44,47,51)
DeadColour = (200,200,200)
White = (255,255,255)
GridColour = (151,151,151)

# Record Data Type for each high score
class highScoreRec():
    def __init__(self, name, number):
        self.name = name
        self.number = number

# Load the .csv file into an array of records
def loadHighScores():
    HighScores = []
    try:
        with open('highscores.csv', 'r+') as scorescsv:
            delimited = csv.reader(scorescsv, delimiter=',')
            for line in delimited:
                if len(HighScores) < 24:
                    HighScores.append(highScoreRec(line[0],line[1]))
                else:
                    return HighScores
    except: # An error will occur in the above if there is no highscores file, therefore create one:
        newfile = open('highscores.csv', 'w+') # 'r+' does not create a file, therefore this must be done'
        newfile.close()
        loadHighScores() # Now try and read it again
    return HighScores


# Save the array of records into a .csv file
def saveHighScores(HighScores):
    with open('highscores.csv', 'w') as scorescsv:
        writer = csv.writer(scorescsv, delimiter=',')
        for i in range(len(HighScores)):
            writer.writerow([HighScores[i].name, HighScores[i].number])

# Sort the array of records in ascending order
def sortHighScores(HighScores): # Simple selection sort
    for j in range(len(HighScores)):
        max = j
        for i in range(j+1, len(HighScores)):
            if int(HighScores[max].number) < int(HighScores[i].number):
                max = i
        HighScores[j], HighScores[max] = HighScores[max], HighScores[j]
    return HighScores

def highScoreInput(screen, HighScores, userNameInput, nameEntered): # Display the user input in a box
    textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 18)
    textFontSubTitle = pygame.font.Font("CG-pixel-4x5.ttf", 10)
    InputBox = pygame.image.load("img/InputBox.png")
    ConfirmMessage = textFontSubTitle.render("Enter To Save", False, DeadColour)
    screen.blit(InputBox,(275,190))
    if userNameInput:
        inputBoxContents = textFontTitle.render("".join(userNameInput), False, DeadColour)
        screen.blit(inputBoxContents,(280,200))
        screen.blit(ConfirmMessage,(280,235))


# Set the speed at which blocks fall and place
def setDifficulty(lines, difficultyTimer):
    if lines < 5:
        return 700
    if lines > 5 and lines < 10:
        return 600
    if lines > 10 and lines < 15:
        return 500
    if lines > 15 and lines < 20:
        return 400
    if lines > 20 and lines < 25:
        return 300
    if lines > 25 and lines < 30:
        return 225
    if lines > 30 and lines < 35:
        return 200
    if lines > 35:
        return 175
    return 700

# Display the array of records
def renderHighScores(HighScores):
    textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 15)
    for i in range(len(HighScores)):
        HighScores[i].number = str(HighScores[i].number).replace("[","")
        HighScores[i].number = str(HighScores[i].number).replace("]","")
        HighScores[i].number = str(HighScores[i].number).replace("'","")
        ScoreNameText = textFontTitle.render(HighScores[i].name, False, DeadColour)
        ScoreNumberText = textFontTitle.render(HighScores[i].number, False, DeadColour)
        screen.blit(ScoreNameText,(50,(80 + (i * 25))))
        screen.blit(ScoreNumberText,(180,(80 + (i* 25))))

# UI design and back button for high score screen
def highScoreScreenButton(screen):
        textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 20)
        TitleImage = textFontTitle.render("Tetris", False, DeadColour)
        screen.blit(TitleImage,(60,20))
        BackButton = pygame.image.load("img/BackButton.png")
        BackButtonActive = pygame.image.load("img/BackButtonActive.png")
        BackButtonRect = BackButton.get_rect(center = (335,90))
        if BackButtonRect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(BackButtonActive,(285,70))
        else:
            screen.blit(BackButton,(285,70))

        return BackButtonRect


# Load the images for the sidebar of the game
def createQueueImages():
    # The pngs used for the instructions screen and the list of upcoming blocks whilst playing
    QueueImages = []
    QueueImages.append(pygame.image.load("img/L_Block.png"))
    QueueImages.append(pygame.image.load("img/J_Block.png"))
    QueueImages.append(pygame.image.load("img/S_Block.png"))
    QueueImages.append(pygame.image.load("img/Z_Block.png"))
    QueueImages.append(pygame.image.load("img/I_Block.png"))
    QueueImages.append(pygame.image.load("img/O_Block.png"))
    QueueImages.append(pygame.image.load("img/T_Block.png"))
    return QueueImages


# Outline of the grid for aesthetic reasons
def renderUnfilledGrid(screen, colour, GridTopleft_x, GridTopleft_y, GridWidth, GridHeight):
    screen.fill(MenuBackground)
    for i in range(0,GridWidth + 1):
        if i == 0 or i == GridWidth:
            pygame.draw.line(screen, colour,[GridTopleft_x + (i*25), GridTopleft_y], [(i*25) + GridTopleft_x, GridTopleft_y + (25*GridHeight)])
    for i in range(0,GridHeight + 1):
        if i == 0 or i == GridHeight:
            pygame.draw.line(screen, colour,[GridTopleft_x, GridTopleft_y + (i*25)], [GridTopleft_x + (25*GridWidth), (i*25 + GridTopleft_y)])

# Main Menu UI Design and Buttons
def mainMenuFunc(screen, colour):
    textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 20)
    TitleImage = textFontTitle.render("Tetris", False, DeadColour)
    PlayButton = pygame.image.load("img/PlayButton.png")
    PlayButtonActive = pygame.image.load("img/PlayButtonActive.png")
    InstructionButton = pygame.image.load("img/InstructionButton.png")
    InstructionButtonActive = pygame.image.load("img/InstructionButtonActive.png")
    ScoreButton = pygame.image.load("img/ScoreButton.png")
    ScoreButtonActive = pygame.image.load("img/ScoreButtonActive.png")
    QuitButton = pygame.image.load("img/QuitButton.png")
    QuitButtonActive = pygame.image.load("img/QuitButtonActive.png")
    screen.blit(TitleImage,(60,20))
    PlayButtonRect = PlayButton.get_rect(center = (335,90))
    InstructionButtonRect = InstructionButton.get_rect(center = (335,140))
    ScoreButtonRect = ScoreButton.get_rect(center = (335, 190))
    QuitButtonRect = QuitButton.get_rect(center = (335, 240))
    if PlayButtonRect.collidepoint(pygame.mouse.get_pos()): # Reactive buttons
        screen.blit(PlayButtonActive,(285,70))
    else:
        screen.blit(PlayButton,(285,70))
    if InstructionButtonRect.collidepoint(pygame.mouse.get_pos()):
        screen.blit(InstructionButtonActive,(285,120))
    else:
        screen.blit(InstructionButton,(285,120))
    if ScoreButtonRect.collidepoint(pygame.mouse.get_pos()):
        screen.blit(ScoreButtonActive,(285,170))
    else:
        screen.blit(ScoreButton,(285,170))
    if QuitButtonRect.collidepoint(pygame.mouse.get_pos()):
        screen.blit(QuitButtonActive,(285,220))
    else:
        screen.blit(QuitButton,(285,220))
    return PlayButtonRect, InstructionButtonRect, QuitButtonRect, ScoreButtonRect




# Draw the empty grid on the main menu
def mainMenuGrid(screen, colour, GridTopleft_x, GridTopleft_y, GridWidth, GridHeight):
        screen.fill(MenuBackground)
        for i in range(0,GridWidth + 1):
                pygame.draw.line(screen, colour,[GridTopleft_x + (i*25), GridTopleft_y], [(i*25) + GridTopleft_x, GridTopleft_y + (25*GridHeight)])
        for i in range(0,GridHeight + 1):
                pygame.draw.line(screen, colour,[GridTopleft_x, GridTopleft_y + (i*25)], [GridTopleft_x + (25*GridWidth), (i*25 + GridTopleft_y)])

# Draw the instructions screen (UI Design and Button)
def Instructions(screen, MenuBackground):
    InstructionsScreenImg = pygame.image.load("img/InstructionScreen.png")
    textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 20)
    TitleImage = textFontTitle.render("Tetris", False, DeadColour)
    BackButton = pygame.image.load("img/BackButton.png")
    BackButtonActive = pygame.image.load("img/BackButtonActive.png")
    screen.blit(TitleImage,(60,20))
    screen.blit(InstructionsScreenImg,(GridTopleft_x+2,GridTopleft_y))
    pygame.draw.rect(screen, MenuBackground, [25, 626, 100, 20], 0)
    BackButtonRect = BackButton.get_rect(center = (335,90))
    if BackButtonRect.collidepoint(pygame.mouse.get_pos()):
        screen.blit(BackButtonActive,(285,70))
    else:
        screen.blit(BackButton,(285,70))
    return BackButtonRect

# UI design for Game Over Screen
def GameOverFunc(screen, menuBackground):
    textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 20)
    TitleImage = textFontTitle.render("Tetris", False, DeadColour)
    screen.blit(TitleImage,(60,20))
    RetryButton = pygame.image.load("img/RetryButton.png")
    RetryButtonActive = pygame.image.load("img/RetryButtonActive.png")
    RetryButtonRect = RetryButton.get_rect(center = (335,90))
    if RetryButtonRect.collidepoint(pygame.mouse.get_pos()):
        screen.blit(RetryButtonActive,(285,70))
    else:
        screen.blit(RetryButton,(285,70))
    BackButton = pygame.image.load("img/BackButton.png")
    BackButtonActive = pygame.image.load("img/BackButtonActive.png")
    BackButtonRect = BackButton.get_rect(center = (335,140))
    if BackButtonRect.collidepoint(pygame.mouse.get_pos()):
        screen.blit(BackButtonActive,(285,120))
    else:
        screen.blit(BackButton,(285,120))
    return RetryButtonRect, BackButtonRect


# Create the shapes array of record
def createShapes():
    # Colours used
    White = (255,255,255)
    Red = (247,48,37)
    Purple = (121, 85, 160)
    Cream = (247, 231, 146)
    Blue = (84, 175, 190)
    Green = (171, 236, 51)
    Dark_Blue = (72, 93, 190)
    Orange = (204, 85, 0)
    # Shape Templates
    L_Block_Template1 = [[0,0,1],
                        [1,1,1]]
    L_Block_Template2 = [[1,0],
                        [1,0],
                        [1,1]]
    L_Block_Template3 = [[1,1,1],
                        [1,0,0]]
    L_Block_Template4 = [[1,1],
                        [0,1],
                        [0,1]]
    J_Block_Template1 = [[1,0,0],
                        [1,1,1]]
    J_Block_Template2 = [[1,1],
                        [1,0],
                        [1,0]]
    J_Block_Template3 = [[1,1,1],
                        [0,0,1]]
    J_Block_Template4 = [[0,1],
                        [0,1],
                        [1,1]]
    S_Block_Template1 = [[0,1,1],
                        [1,1,0]]
    S_Block_Template2 = [[1,0],
                        [1,1],
                        [0,1]]
    Z_Block_Template1 = [[1,1,0],
                        [0,1,1]]
    Z_Block_Template2 = [[0,1],
                        [1,1],
                        [1,0]]
    I_Block_Template1 = [[1],
                        [1],
                        [1],
                        [1]]
    I_Block_Template2 = [[1,1,1,1]]
    O_Block_Template1 = [[1,1],
                        [1,1]]
    T_Block_Template1 = [[0,1,0],
                        [1,1,1],
                        [0,0,0]]
    T_Block_Template2 = [[0,1,0],
                        [0,1,1],
                        [0,1,0]]
    T_Block_Template3 = [[0,0,0],
                        [1,1,1],
                        [0,1,0]]
    T_Block_Template4 = [[0,1,0],
                        [1,1,0],
                        [0,1,0]]
    class Shape(): # Array of records for the shape, containing it's template + rotations and it's colour
        def __init__(self, template, colour, name):
            self.block = template
            self.colour = colour
            self.name = name
    # Assigns each array of records to a list, each containing various rotations.
    L_Block = []
    L_Block.append(Shape(L_Block_Template1, Orange, "L_Block"))
    L_Block.append(Shape(L_Block_Template2, Orange, "L_Block"))
    L_Block.append(Shape(L_Block_Template3, Orange, "L_Block"))
    L_Block.append(Shape(L_Block_Template4, Orange, "L_Block"))
    J_Block = []
    J_Block.append(Shape(J_Block_Template1, Dark_Blue, "J_Block"))
    J_Block.append(Shape(J_Block_Template2, Dark_Blue, "J_Block"))
    J_Block.append(Shape(J_Block_Template3, Dark_Blue, "J_Block"))
    J_Block.append(Shape(J_Block_Template4, Dark_Blue, "J_Block"))
    S_Block = []
    S_Block.append(Shape(S_Block_Template1, Green, "S_Block"))
    S_Block.append(Shape(S_Block_Template2, Green, "S_Block"))
    Z_Block = []
    Z_Block.append(Shape(Z_Block_Template1, Red, "Z_Block"))
    Z_Block.append(Shape(Z_Block_Template2, Red, "Z_Block"))
    I_Block = []
    I_Block.append(Shape(I_Block_Template1, Blue, "I_Block"))
    I_Block.append(Shape(I_Block_Template2, Blue, "I_Block"))
    O_Block = []
    O_Block.append(Shape(O_Block_Template1, Cream, "O_Block"))
    T_Block = []
    T_Block.append(Shape(T_Block_Template1, Purple, "T_Block"))
    T_Block.append(Shape(T_Block_Template2, Purple, "T_Block"))
    T_Block.append(Shape(T_Block_Template3, Purple, "T_Block"))
    T_Block.append(Shape(T_Block_Template4, Purple, "T_Block"))

    # The array of different shapes
    Shapes = [L_Block, J_Block, S_Block, Z_Block, I_Block, O_Block, T_Block]
    # These shapes can then be spawned using: Shapes[shape][rotation].block
    return Shapes

# Create the two grids used by the game
def createStaticGrids(GridHeight, Gridwidth):
    activeGrid = CreateGrid(GridHeight, GridWidth)
    inactiveGrid = CreateGrid(GridHeight, GridWidth)
    return activeGrid, inactiveGrid

# Two loops, for each set of lines forming rows and columns
def renderGrid(screen, colour, GridTopleft_x, GridTopleft_y, GridWidth, GridHeight):
    for i in range(0,GridWidth + 1):
        pygame.draw.line(screen, colour,[GridTopleft_x + (i*25), GridTopleft_y], [(i*25) + GridTopleft_x, GridTopleft_y + (25*GridHeight)])
    for i in range(0,GridHeight + 1):
        pygame.draw.line(screen, colour,[GridTopleft_x, GridTopleft_y + (i*25)], [GridTopleft_x + (25*GridWidth), (i*25 + GridTopleft_y)])

# Returns true if the active grid is empty.
def checkActiveGrid(grid):
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == 1:
                return False
    return True


# Creates a nested list of the grid, with each square storing a boolean value.
def CreateGrid(GridHeight, GridWidth):
    grid = []
    for rows in range(0,GridHeight):
        row = []
        for cols in range (0,GridWidth):
            row.append(0)
        grid.append(row)
    return grid

# For each block on the grid set to true, render that block
def renderBlocks(grid, screen, colour, GridTopleft_x, GridTopleft_y):
    blockWidth = 25
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == 1:
                pygame.draw.rect(screen, colour, [GridTopleft_x + (blockWidth * col),GridTopleft_y + (blockWidth * row),blockWidth,blockWidth])

# Display UI elements in pre set positions
def renderMenuElements(score):
    BigBox = pygame.image.load("img/BigBox.png")
    ScoreBox = pygame.image.load("img/box.png")
    RegularBox = pygame.image.load("img/RegularBox.png")
    textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 20)
    textFontNumber = pygame.font.Font("CG-pixel-4x5.ttf", 17)
    TitleImage = textFontTitle.render("Tetris", False, DeadColour)
    screen.blit(TitleImage,(60,20))
    score_title = textFontTitle.render("Score:", False, DeadColour)
    score_counter = textFontNumber.render(str(score), False, DeadColour)
    Queue_title = textFontTitle.render("Queue:", False, DeadColour)
    Hold_Title = textFontTitle.render("Hold:", False, DeadColour)
    screen.blit(RegularBox,(285,550))
    screen.blit(BigBox,(285,200))
    screen.blit(score_title,(285,70))
    screen.blit(score_counter,(290,110))
    screen.blit(Queue_title,(285,160))
    screen.blit(Hold_Title,(285,520))
    screen.blit(ScoreBox,(285,100))

# Display the score on the game over screen
def renderGameOverScore(score):
    ScoreBox = pygame.image.load("img/box.png")
    textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 20)
    textFontNumber = pygame.font.Font("CG-pixel-4x5.ttf", 17)
    textfontSubTitle = pygame.font.Font("CG-pixel-4x5.ttf", 12)
    highscoreboxTitle = textfontSubTitle.render("Enter name:", False, DeadColour)
    score_counter = textFontTitle.render(str(score), False, DeadColour)
    score_title = textFontTitle.render("Score:", False, DeadColour)
    screen.blit(highscoreboxTitle,(280,170))
    screen.blit(score_title,(285,260))
    screen.blit(ScoreBox,(285,290))
    screen.blit(score_counter,(290,300))


# Display PNGs representing each item in the upcoming blocks queue
def renderQueue(queue):
        for i in range(len(queue)):
            screen.blit(QueueImages[convertBlockNameToIndex(queue[i])],(290, (200 + (i * 75))))

# Display what block is currently being held
def renderHold(heldBlock):
    if heldBlock:
        screen.blit(QueueImages[convertBlockNameToIndex(heldBlock)],(290,560))

# Check if a block has exceeded the height of the grid
def checkGameOver(inactiveGrid):
    for col in range(len(inactiveGrid[0])):
        if inactiveGrid[0][col] == 1:
            return True

# Clear full rows, return how many rows were cleared
def clearFullRows(inactiveGrid):
    fullRowCounter = 0
    marker = 0
    for row in range(len(inactiveGrid)):
        if all(inactiveGrid[row]):
            fullRowCounter = fullRowCounter + 1 # Count how many rows are full this turn

    for fullRows in range(fullRowCounter): # Repeat one row at a time
        for row in range(len(inactiveGrid)):
            if all(inactiveGrid[row]):
                marker = row
                for col in range(len(inactiveGrid[0])):
                    inactiveGrid[row][col] = 0 # Clear ONE row
                break
        for row in range(marker,-1,-1):
            for col in range(len(inactiveGrid[0])):
                if inactiveGrid[row][col] == 1:
                    inactiveGrid[row][col] = 0
                    inactiveGrid[row+1][col] = 1 # Shift ONE row down
    return fullRowCounter

# For each row cleared, increment the player's score accordingly
def incrementScore(fullRowCounter):
    score = 50 * (fullRowCounter ** 2) + 50 * fullRowCounter
    return score

# Fill a list with randomly picked shapes
def topUpQueue(Shapes, queue): # List of names
    while len(queue) < 4:
        randShape = random.randint(0,6)
        queue.append(Shapes[randShape][0].name)
    return queue

# Used to find the index of shapes in the Shapes list, given their name.
def convertBlockNameToIndex(Name):
    if Name == "L_Block":
        return 0
    elif Name == "J_Block":
        return 1
    elif Name == "S_Block":
        return 2
    elif Name == "Z_Block":
        return 3
    elif Name == "I_Block":
        return 4
    elif Name == "O_Block":
        return 5
    elif Name == "T_Block":
        return 6
    else:
        return 0

# Spawn a block from the queue in the top centre of the grid.
def spawnBlock(queue, grid):
    topLeftX = 4
    topLeftY = 0
    activeBlockName = queue[0]
    activeBlockRotation = 0
    activeBlockColour = Shapes[convertBlockNameToIndex(queue[0])][0].colour
    activeBlockTemplate = Shapes[convertBlockNameToIndex(queue[0])][0].block
    for row in range(0,len(activeBlockTemplate)):
        for col in range(0,len(activeBlockTemplate[0])):
            grid[row][4+col] = activeBlockTemplate[row][col]
    del queue[0]
    return activeBlockRotation, activeBlockName, activeBlockColour, grid, topLeftX, topLeftY, False

# Shifts all blocks in the activeGrid to the right, and checks for collissions with other blocks and the boundaries of the grid
def moveBlockRight(activeBlockName, activeGrid, topLeftX):
    tempGrid = activeGrid
    validRows = [] # The rows of active blocks that can be moved to the right successfully
    validCols = []
    activeBlockCounter = 0 # Number of blocks detected this scan
    for row in range(len(tempGrid) - 1, -1, -1):
        for col in range(len(tempGrid[0]) - 1, -1, -1):
            if tempGrid[row][col] == 1:
                activeBlockCounter = activeBlockCounter + 1
                if col + 1 != len(tempGrid[0]):
                    if inactiveGrid[row][col+1] == 0:
                        validRows.append(row)
                        validCols.append(col) # Valid rows and cols are saved for later, as to not cause blocks to become disjointed
                    else:
                        return topLeftX, False # the X coordinate of the top left most block is returned, as is whether or not the move to the right was made
                else:
                    return topLeftX, False
            if activeBlockCounter == 4: # Once all the blocks have been detected this scan
                if validRows:
                    topLeftX = topLeftX + 1
                    for i in range(len(validRows)):
                        activeGrid[validRows[i]][validCols[i]] = 0
                        activeGrid[validRows[i]][validCols[i] + 1] = 1
                    validRows[:] = []
                    validCols[:] = []
                    return topLeftX, True
    return topLeftX, False


# Same as above, but for the left
def moveBlockLeft(activeBlockName, activeGrid, topLeftX):
    tempGrid = activeGrid
    validRows = []
    validCols = []
    activeBlockCounter = 0
    for row in range(len(tempGrid)):
        for col in range(len(tempGrid[0])):
            if tempGrid[row][col] == 1:
                activeBlockCounter = activeBlockCounter + 1
                if col - 1 != -1:
                    if inactiveGrid[row][col-1] == 0:
                        validRows.append(row)
                        validCols.append(col)
                    else:
                        return topLeftX, False
                else:
                    return topLeftX, False
            if activeBlockCounter == 4:
                if validRows:
                    topLeftX = topLeftX - 1
                    for i in range(len(validRows)):
                        activeGrid[validRows[i]][validCols[i]] = 0
                        activeGrid[validRows[i]][validCols[i] - 1] = 1
                    validRows[:] = []
                    validCols[:] = []
                    return topLeftX, True
    return topLeftX, False


# Move the blocks on the active grid down. Same formula for saving valid rows and columns as previously used
def DropBlock(activeGrid, inactiveGrid, topLeftY):
    validRows = []
    validCols = []
    tempGrid = activeGrid
    activeBlockCounter = 0
    for row in range(len(tempGrid) - 1, -1, -1): # Scan from the left to right
        for col in range(len(tempGrid[0])- 1, -1, -1): # Scan from the bottom to the top
            if tempGrid[row][col] == 1:
                activeBlockCounter = activeBlockCounter + 1
                if row + 1 != len(tempGrid):
                    if inactiveGrid[row+1][col] == 0:
                        validRows.append(row)
                        validCols.append(col)
                    else:
                        placeBlock(activeGrid, inactiveGrid)
                        return topLeftY
                else:
                    placeBlock(activeGrid, inactiveGrid)
                    return topLeftY
            if activeBlockCounter == 4:
                if validRows:
                    for i in range(len(validRows)):
                        activeGrid[validRows[i]][validCols[i]] = 0
                        activeGrid[validRows[i]+1][validCols[i]] = 1
                    validRows[:] = []
                    validCols[:] = []
                    topLeftY = topLeftY + 1
                    return topLeftY
    return topLeftY

# If there are no collisions, clear the grid and spawn in the next rotation
def rotateBlock(activeBlockName, activeGrid, activeBlockRotation, topLeftX, topLeftY, inactiveGrid):
    activeBlockRotation = activeBlockRotation + 1 # Move to the next rotation
    activeBlockIndex = convertBlockNameToIndex(activeBlockName) # Get the Shapes[] index of the current shape
    nextRotationTemplate = Shapes[activeBlockIndex][activeBlockRotation % len(Shapes[activeBlockIndex])].block # Get the next rotation template for the current block. Modulo is used to provide an looping list of these rotations
    topLeftX, topLeftY, activeBlockRotation, rotationBool = checkRotation(topLeftX, topLeftY, activeBlockRotation, activeGrid, inactiveGrid, nextRotationTemplate, activeBlockIndex) # Check for rotation collision with the boundaries of the grid
    inactiveGridBool, topLeftY = checkRotationCollision(nextRotationTemplate, inactiveGrid, topLeftX, topLeftY) # Check if the upcoming rotation collides with the other blocks on the grid
    if inactiveGridBool: # if there is no collission with other blocks
        if rotationBool: # If there is no collission with the boundaries of the grid

            for row in range(0,len(activeGrid)): # Clear the blocks from the previous rotation
                for col in range(0,len(activeGrid[0])):
                    if activeGrid[row][col] == 1:
                        activeGrid[row][col] = 0

            for row in range(0,len(nextRotationTemplate)): # Spawn in the new rotation
                for col in range(0,len(nextRotationTemplate[0])):
                    activeGrid[topLeftY+row][topLeftX+col] = nextRotationTemplate[row][col]

            return topLeftX, topLeftY, activeBlockRotation # Success

        else:
            return topLeftX, topLeftY, activeBlockRotation - 1 # If invalid rotation, return the previous rotation
    else:
        return topLeftX, topLeftY, activeBlockRotation - 1

# Checks to see if the next rotation collides with the boundaries of the grid
def checkRotation(topLeftX, topLeftY, activeBlockRotation, grid, inactiveGrid, nextRotationTemplate,activeBlockIndex):
        for i in range(0,len(nextRotationTemplate[0])): # for the width of new rotation, see if it exceeds the width of the grid
            if topLeftX+i < 0:
                topLeftX, RightMovementSuccess = moveBlockRight(activeBlockName, activeGrid, topLeftX)
                if RightMovementSuccess:
                    return topLeftX, topLeftY, activeBlockRotation, True # Return the X and Y coordinates of the block, the rotation being made, and whether or not the block was moved.
                else:
                    return topLeftX, topLeftY, activeBlockRotation, False
            if topLeftX+i > len(grid[0])-1:
                topLeftX, LeftMovementSuccess = moveBlockLeft(activeBlockName, activeGrid, topLeftX)
                if LeftMovementSuccess:
                    return topLeftX, topLeftY, activeBlockRotation, True
                else:
                    return topLeftX, topLeftY, activeBlockRotation, False
        for i in range(0,len(nextRotationTemplate)): # For the height of the new rotation, see if it exceeds the height of the grid
            if topLeftY+i < 0 or topLeftY+i > len(grid)-1:
                return topLeftX, topLeftY, activeBlockRotation, False
        return topLeftX, topLeftY, activeBlockRotation, True

# See if the new rotation collides with blocks on the inactiveGrid
def checkRotationCollision(nextRotationTemplate, inactiveGrid, topLeftX, topLeftY):
    try: # To handle exceptions when testing a block that would rotate outside of the grid
        checkingGrid = CreateGrid(len(inactiveGrid),len(inactiveGrid[0]))
        for row in range(0,len(nextRotationTemplate)):
            for col in range(0,len(nextRotationTemplate[0])):
                checkingGrid[topLeftY+row][topLeftX+col] = nextRotationTemplate[row][col]
        for row in range(0,len(inactiveGrid)):
            for col in range(0,len(inactiveGrid[0])):
                if checkingGrid[row][col] == 1:
                    if inactiveGrid[row][col] == 1:
                        return False, topLeftY
    except:
        return False, topLeftY
    return True, topLeftY

# Drop the block down as many rows as there are in the grid
def hardDropBlock(activeGrid, inactiveGrid):
    topLeftY = 0
    for i in range(len(activeGrid)):
        topLeftY = DropBlock(activeGrid, inactiveGrid, topLeftY)

# Transfer the block to the inactiveGrid
def placeBlock(activeGrid, inactiveGrid):
    for row in range(len(activeGrid)):
        for col in range(len(activeGrid[row])):
            if activeGrid[row][col] == 1:
                activeGrid[row][col] = 0
                inactiveGrid[row][col] = 1

# Activate this function to place the currently active block into storage, which can then be swapped into play later. Can only be used once per turn.
def holdBlock(queue, activeBlockName, heldBlock, activeGrid, Shapes, holdUsed):
        # activeBlockIndex = convertBlockNameToIndex(activeBlockName)
    if heldBlock == 0:
        heldBlock = activeBlockName
        for row in range(0,len(activeGrid)): # Clear the blocks from the previous rotation
            for col in range(0,len(activeGrid[0])):
                if activeGrid[row][col] == 1:
                    activeGrid[row][col] = 0
        activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, hold_removed = spawnBlock(queue, activeGrid)
        queue = topUpQueue(Shapes, queue)
        return activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, heldBlock, queue, True
    else:
        tempBlockName = activeBlockName
        queue.insert(0,heldBlock)
        for row in range(0,len(activeGrid)): # Clear the blocks from the previous rotation
            for col in range(0,len(activeGrid[0])):
                if activeGrid[row][col] == 1:
                    activeGrid[row][col] = 0
        activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, hold_removed = spawnBlock(queue, activeGrid)
        heldBlock = tempBlockName
        return activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, heldBlock, queue, True



# Pygame Mainline Loop
HighScores = loadHighScores()
while running == True:
    clock.tick(60)
    scanTicker = clock.get_time()
    for event in pygame.event.get():
        # The controls for the game
        if event.type == pygame.QUIT:
            running == False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if mainMenu:
                running = False
            else:
                mainMenu = True
                InstructionsScreen = False
                playingGame = False
                HighScoreScreen = False
                gameOver = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and not gameOver:
            # Restart the game
            mainMenu = False
            queue = []
            Shapes = createShapes()
            QueueImages = createQueueImages()
            playingGame = True
            score = 0
            lines = 0
            difficultyTimer = 700
            scoreSaved = False
            userNameInput = []
            activeGrid, inactiveGrid = createStaticGrids(GridHeight, GridWidth)
            queue = topUpQueue(Shapes, queue)
            activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, holdUsed = spawnBlock(queue, activeGrid)
            queue = topUpQueue(Shapes, queue)
            heldBlock = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and playingGame:
            topLeftX, topLeftY, activeBlockRotation = rotateBlock(activeBlockName, activeGrid, activeBlockRotation, topLeftX, topLeftY, inactiveGrid)
            # print("TOP LEFT X IS", topLeftX, "- TOP LEFT Y IS", topLeftY, "- ActiveBlockRotation is", activeBlockRotation)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT and playingGame:
            topLeftX, RightMovementSuccess = moveBlockRight(activeBlockName, activeGrid, topLeftX)
            # print("TOP LEFT X IS", topLeftX, "- TOP LEFT Y IS", topLeftY, "- ActiveBlockRotation is", activeBlockRotation)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT and playingGame:
            topLeftX, LeftMovementSuccess= moveBlockLeft(activeBlockName, activeGrid, topLeftX)
            # print("TOP LEFT X IS", topLeftX, "- TOP LEFT Y IS", topLeftY, "- ActiveBlockRotation is", activeBlockRotation)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and playingGame:
            hardDropBlock(activeGrid, inactiveGrid)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN and playingGame:
            topLeftY = DropBlock(activeGrid, inactiveGrid, topLeftY)
            # print("TOP LEFT X IS", topLeftX, "- TOP LEFT Y IS", topLeftY, "- ActiveBlockRotation is", activeBlockRotation)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c and playingGame:
            if not holdUsed:
                activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, heldBlock, queue, holdUsed = holdBlock(queue, activeBlockName, heldBlock, activeGrid, Shapes, holdUsed)
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            print("(",x,",",y,")")
        if event.type == pygame.MOUSEBUTTONDOWN and mainMenu:
            if PlayButtonRect.collidepoint(event.pos):
                # Restart the game
                mainMenu = False
                queue = []
                Shapes = createShapes()
                QueueImages = createQueueImages()
                playingGame = True
                score = 0
                lines = 0
                difficultyTimer = 400
                scoreSaved = False
                userNameInput = []
                activeGrid, inactiveGrid = createStaticGrids(GridHeight, GridWidth)
                queue = topUpQueue(Shapes, queue)
                activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, holdUsed = spawnBlock(queue, activeGrid)
                queue = topUpQueue(Shapes, queue)
                heldBlock = False
            elif InstructionButtonRect.collidepoint(event.pos):
                mainMenu = False
                InstructionsScreen = True
                playingGame = False
                break
            elif ScoreButtonRect.collidepoint(event.pos):
                mainMenu = False
                InstructionsScreen = False
                playingGame = False
                HighScoreScreen = True
                HighScores = sortHighScores(HighScores)
                break
            elif QuitButtonRect.collidepoint(event.pos):
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN and InstructionsScreen:
            if BackButtonRect.collidepoint(event.pos):
                InstructionsScreen = False
                mainMenu = True
                playingGame = False
                gameOver = False
                HighScoreScreen = False
                break
        if event.type == pygame.MOUSEBUTTONDOWN and gameOver:
            if RetryButtonRect.collidepoint(event.pos):
                # Restart the game
                mainMenu = False
                gameOver = False
                queue = []
                Shapes = createShapes()
                QueueImages = createQueueImages()
                playingGame = True
                score = 0
                lines = 0
                difficultyTimer = 700
                scoreSaved = False
                userNameInput = []
                activeGrid, inactiveGrid = createStaticGrids(GridHeight, GridWidth)
                queue = topUpQueue(Shapes, queue)
                activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, holdUsed = spawnBlock(queue, activeGrid)
                queue = topUpQueue(Shapes, queue)
                heldBlock = False
            if BackButtonRect.collidepoint(event.pos):
                InstructionsScreen = False
                mainMenu = True
                playingGame = False
                gameOver = False
        if event.type == pygame.MOUSEBUTTONDOWN and HighScoreScreen:
            if BackButtonRect.collidepoint(event.pos):
                InstructionsScreen = False
                HighScoreScreen = False
                mainMenu = True
                playingGame = False
        if event.type == pygame.KEYDOWN and gameOver and nameEntered == False and score != 0:
            if event.key != pygame.K_DELETE and event.key != pygame.K_BACKSPACE and event.key != pygame.K_RETURN:
                if len(userNameInput) < 5:
                    if event.unicode.isalnum():
                        userNameInput.append(event.unicode) # Username input
            elif event.key == pygame.K_RETURN:
                userNameInput = "".join(userNameInput)
                nameEntered = True
            elif event.key == pygame.K_BACKSPACE:
                if len(userNameInput) > 0:
                    del userNameInput[len(userNameInput)-1]




    if mainMenu:
        mainMenuGrid(screen, GridColour, GridTopleft_x, GridTopleft_y, GridWidth, GridHeight)
        PlayButtonRect, InstructionButtonRect, QuitButtonRect, ScoreButtonRect = mainMenuFunc(screen, White)

    elif playingGame:
        screen.fill(MenuBackground) # Colour the background
        renderBlocks(activeGrid, screen, activeBlockColour, GridTopleft_x, GridTopleft_y) # Display blocks on the active grid
        renderBlocks(inactiveGrid, screen, DeadColour, GridTopleft_x, GridTopleft_y) # Display the blocks on the inactive Grid
        renderGrid(screen, GridColour, GridTopleft_x, GridTopleft_y, GridWidth, GridHeight) # Display the lines forming the grid
        renderMenuElements(score) # Display UI elements
        renderQueue(queue) # Display Queue
        renderHold(heldBlock)
        dropTicker = dropTicker + scanTicker # Increment tick controlling the rate at which blocks fall
        if checkActiveGrid(activeGrid): # If the active grid is empty
            fullRowCounter = clearFullRows(inactiveGrid) # Count the number of rows cleared, if any
            if fullRowCounter > 0: # If a block has been cleared
                score = score + incrementScore(fullRowCounter)
                lines = lines + fullRowCounter
                difficultyTimer = setDifficulty(lines, difficultyTimer)
            if checkGameOver(inactiveGrid): # Check for game over
                playingGame = False # Halt the function of the game
                gameOver = True
                nameEntered = False
                userNameInput = []
            else:
                activeBlockRotation, activeBlockName, activeBlockColour, activeGrid, topLeftX, topLeftY, holdUsed = spawnBlock(queue, activeGrid)
                queue = topUpQueue(Shapes, queue)
        elif dropTicker > difficultyTimer:
            topLeftY = DropBlock(activeGrid, inactiveGrid, topLeftY)
            dropTicker = 0

    elif gameOver:
        screen.fill(MenuBackground)
        renderBlocks(inactiveGrid, screen, DeadColour, GridTopleft_x, GridTopleft_y) # Display the blocks on the inactive Grid
        renderGrid(screen, GridColour, GridTopleft_x, GridTopleft_y, GridWidth, GridHeight) # Display the lines forming the grid
        RetryButtonRect, BackButtonRect = GameOverFunc(screen, MenuBackground)
        renderGameOverScore(score)
        if score != 0:
            if not nameEntered:
                highScoreInput(screen, HighScores, userNameInput, nameEntered)
            if nameEntered:
                textFontTitle = pygame.font.Font("CG-pixel-4x5.ttf", 20)
                SavedMsg = textFontTitle.render("Saved!", False, DeadColour)
                screen.blit(SavedMsg,(285,200))
                if not scoreSaved:
                    if len(HighScores) < 23:
                        HighScores.append(highScoreRec(userNameInput, score))
                        scoreSaved = True
                    else:
                        sortHighScores(HighScores)
                        if int(HighScores[len(HighScores) - 1].number) < score:
                            del HighScores[len(HighScores) - 1]
                            HighScores.append(highScoreRec(userNameInput, score))
                            scoreSaved = True



    elif InstructionsScreen:
        renderUnfilledGrid(screen, GridColour, GridTopleft_x, GridTopleft_y, GridWidth, GridHeight)
        BackButtonRect = Instructions(screen, MenuBackground)

    elif HighScoreScreen:
        screen.fill(MenuBackground)
        renderUnfilledGrid(screen, GridColour, GridTopleft_x, GridTopleft_y, GridWidth, GridHeight)
        BackButtonRect = highScoreScreenButton(screen)
        renderHighScores(HighScores)






    pygame.display.flip() # Display requisite


saveHighScores(HighScores)
pygame.display.quit()
