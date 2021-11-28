# Alex Wills
# 15 Nov 2020 Updated
# Completed 24 Nov 2020
# 
# game.py
# What what what! it's Tetris! Plays a Tetris game with 10 levels
#   of increasing difficulty. Called Quadtris for copyright avoidance.
#
# Credits to Alexey Pajitnov for original game design of Tetris
#         to John Zelle for the graphics.py package
#         to Professor Eaton for teaching me everything I know about Python
#         to Python for being helpful for this project
#         to Hope for always being there for me <3
#         to Jacob for being a fellow Tetris fan and inspiring this journey
#         to Eirinn for putting up with me and Jacob and our Tetris
#         to Ray for teaching me epic key shortcuts
#         to Lucas for playtesting
#         to Tetris for giving me the chance to win $5 on their mobile Tetris app
#         to Honest Tea and Sparkling Ice for quenching my thirst
#         to the Metz crew for giving me food (shoutouts to Kevin)
#
# To run: Open the terminal at this file location and type "py game.py"

import graphics as gr
import time
import random
import quadrominos as quad


class PlayGrid():
    ''' A data structure to manage the grid for collision detection. Stores blocks and their locations,
    as well as the upcoming Quadrominos and the Quadromino on hold.
    The game will have one PlayGrid instantiated to manage the game.'''
    def __init__(self, cols, rows):
        ''' Creates a 2D array with rows number of rows and cols number of columns
        INPUT
        cols (int) the number of columns in the grid
        rows (int) the number of rows  in the grid
        
        OUTPUT (PlayGrid) an empty PlayGrid object is initialized'''
        self.grid = []
        for row in range(rows):
            row = []
            for i in range(cols):
                row.append(None)
            self.grid.append(row)
       
        self.up_next = []    # Stores the next 7 - 14 pieces (pieces are not random)
        self.held_piece = None  # The player can hold a piece
        self.game_over = False
        self.num_line_clears = 0
        self.score = 0

    def getScore(self):
        ''' Returns the current score (int)'''
        return self.score

    def getNumLines(self):
        ''' Returns the number of lines that have been cleared so far (int)'''
        return self.num_line_clears

    def gameActive(self):
        ''' Returns true if the game is active, false if there is a game over (bool) '''
        return not self.game_over
                
    def gameOver(self):
        ''' Sets self.game_over to true '''
        self.game_over = True

    def getSpace(self, col, row):
        ''' Returns the object at the specified location of the grid 
        INPUT
        col (int) [0, 9] - the column number to search
        row (int) [0, 19] - the row number to search

        Possible Outputs: None
                          Block object'''
        return self.grid[row][col]

    def setSpace(self, block):
        ''' Sets the space occupied by a Block to the Block
        INPUT
        block (Block) - the Block object to lock into place
        
        OUTPUT
        if the Block cannot be locked in (space out of bounds or already occupied), set game_over
        to True
        Saves the Block object to it's location on PlayGrid '''
        row = block.getRowPos()
        col = block.getColPos()
        if row < 0 or self.spaceOccupied(col, row):
            # game over if out of bounds or if space is already occupied
            self.game_over = True
            if row >= 0: # if it is in-bounds, undraw the existing block
                self.getSpace(col, row).undraw()

        self.grid[row][col] = block

    def spaceOccupied(self, col, row):
        ''' Returns true if the space is occupied by a non-zero value
        OR returns true if space is out of bounds (piece is unable to move there)
        INPUT
        col (int) [0, 9] - the column number to search
        row (int) [0, 19] - the row number to search
        
        OUPUT
        bool representing if the specified space is occupied'''
        value = True
        if col >= 0 and row >= 0 and col < 10 and row < 20:
            if self.grid[row][col] == None:
                value = False
        # Allow blocks to go on top of screen by not checking out of bounds above the Grid
        elif row < 0:
            value = False
        return value

    def getNextQuadromino(self, window):
        ''' Returns the next Quadromino and removes it from the up_next list 
        INPUT
        window (gr.GraphWin) - the graphics window
        
        OUTPUT
        piece (Quadromino) - the next piece to enter play'''
        # Get next piece, undraw its mini icon, and draw the next mini icon
        piece = self.up_next.pop(0)
        piece.undrawMini()
        self.up_next[0].drawMiniIcon(window, 0)
        # Ensure there are at least 7 pieces up_next
        if len(self.up_next) < 7:
            self.replenishQuadrominos()
        
        return piece
    
    def replenishQuadrominos(self):
        ''' Refills the up_next list of Quadrominos
        Adds one of each Quadromino shape to the list of upcoming pieces.
        The Quadrominos are added in a random order 
        
        NO INPUT/OUTPUT'''
        seven_pieces = [quad.SQuadromino(), quad.ZQuadromino(), quad.JQuadromino(), quad.LQuadromino(),
                        quad.TQuadromino(), quad.OQuadromino(), quad.IQuadromino()]
        while(len(seven_pieces) > 0):
            # Choose a random piece from the ordered list and move it to the up_next list
            index = random.randint(0, len(seven_pieces) - 1)
            piece = seven_pieces.pop(index)
            self.up_next.append(piece)

    def shiftDown(self, row): 
        ''' Shifts all rows above the given one down by 1 row 
        INPUT
        row (int) [0, 19] - a row that should be recently cleared and empty'''
        # Start at the cleared line, work way up
        while(row > 0):
            # Alias line and line above (lists passed by reference)
            working_row = self.grid[row]
            above_row = self.grid[row - 1]
            # Copy row down, moving any blocks down
            for index in range(0, len(above_row)):
                # If space has a block, move the block
                if not above_row[index] == None:
                    above_row[index].move(0, 1)
                working_row[index] = above_row[index]
            row -= 1
        
        # Clear the top line
        for index in range(0, len(self.grid[0])):
            self.grid[0][index] = None

    def clearRow(self, row):
        ''' Clears a row on the grid and moves every row above down 
        INPUT
        row (int) [0, 19] - the row to be cleared'''
        # Set all of the row to None and shift the above rows down
        for index in range(0, len(self.grid[row])):
            # If theres a block, undraw the block
            if not self.grid[row][index] == None:
                self.grid[row][index].undraw()
            self.grid[row][index] = None
        self.shiftDown(row)

    def clearLines(self, win):
        ''' Goes through the grid and clears any rows that are full, adding points to the score
        and shifting all rows as necessary 
        INPUT
        win (gr.GraphWin) - the graphics window in use'''
        full_rows = []
        # Check every row for fullness
        for row_num in range(0, 20):
            # If any space is empty, all_blocks is False
            all_blocks = True
            for space in self.grid[row_num]:
                if space == None:
                    all_blocks = False
                
            # Add any full rows to a list
            if all_blocks:
                full_rows.append(row_num)

        # Clear rows one at a time
        for row in full_rows:
            for block in self.grid[row]:
                block.setColor("white")
            win.update()
            time.sleep(0.1)
            self.clearRow(row)
        
        # Update score and line clears
        self.num_line_clears += len(full_rows)
        self.score += (len(full_rows)**2) * 100

    def showUpNext(self, window):
        ''' Displays the next piece by the corner of the grid 
        INPUT
        window (gr.GraphWin) - the graphics window in use'''
        # draw the mini icon for the next piece
        next_piece = self.up_next[0]
        next_piece.drawMiniIcon(window, 0)

    def holdQuadromino(self, piece, window):
        ''' Swaps the current piece with the piece in the "hold" position. 
        Returns the next piece if possible (update the active piece)
        INPUT
        piece (Quadromino) - the current active piece in play
        window (gr.GraphWin) - the graphics window in use
        
        OUTPUT
        next_piece (Quadromino) - replacement for the current active piece in play'''
        next_piece = piece  # If piece cannot hold, it returns the same piece.
        if piece.canHold():
            piece.setCanHold(False)
            # Reset current piece
            piece.resetPiece(self)
            # Get the held piece/make a new one, and hold the current piece
            # Undraw the old mini icon, draw the new one
            if self.held_piece == None:  
                next_piece = self.getNextQuadromino(window)
                self.held_piece = piece
            else:
                next_piece = self.held_piece
                self.held_piece.undrawMini()
                self.held_piece = piece
            self.held_piece.drawMiniIcon(window, 1)
        # Undraw current piece, return/swap out with next piece
        piece.undraw()
        next_piece.draw(window) # If canHold == False, piece will simply redraw with no noticable change
        return next_piece

    def __str__(self):
        ''' String method for debugging '''
        string = ""
        for row in self.grid:
            string += str(row) + "\n"
        return string

def drawGradient(window, red, green, blue):
    '''Creates a 10 stage gradient accros the bakcground from the given RGB values to white
    INPUT
    window (gr.GraphWin) - the graphics window in use
    red (int) [0, 255]  
    green (int) [0, 255]  
    blue (int) [0, 255] --- these are the RGB values for the background '''
    height = int(window.getHeight() / 10)
    color = gr.color_rgb(red, green, blue)

    # 10 Rectangles, each with a different color and a different y-coordinate
    for starting_y in range(0, window.getHeight(), height):
        rect = gr.Rectangle(gr.Point(0, starting_y), gr.Point(window.getWidth(), starting_y + height))
        rect.setFill(color)
        rect.setOutline(color)
        rect.draw(window)

        # Update color
        red = int((red + 230) / 2)
        green = int((green + 230) / 2)
        blue = int((blue + 230) / 2)
        color = gr.color_rgb(red, green, blue)
    
def drawPlayField(window):
    ''' Creates a 10x20 grid where each space is 20 x 20 pixels 
    INPUT
    window (gr.GraphWin) - the graphics window in use'''
    play_field = gr.Rectangle(gr.Point(300, 200), gr.Point(500, 600))
    play_field.setFill("#7A7A7A")
    play_field.draw(window)

    # Create vertical lines
    for x_pos in range(320, 500, 20):
        point1 = gr.Point(x_pos, 200)
        point2 = gr.Point(x_pos, 600)
        line = gr.Line(point1, point2)
        line.setOutline("#5C5C5C")
        line.draw(window)

    # Create horizontal lines
    for y_pos in range(220, 600, 20):
        point1 = gr.Point(300, y_pos)
        point2 = gr.Point(500, y_pos)
        line = gr.Line(point1, point2)
        line.setOutline("#5C5C5C")
        line.draw(window)
    
    # Create "Up Next" space:
    little_box = gr.Rectangle(gr.Point(505, 200), gr.Point(585, 280))
    little_box.setFill("#7A7A7A")
    next_text = gr.Text(gr.Point(545, 210), "NEXT")
    next_text.setTextColor("white")
    next_text.setStyle("italic")
    little_box.draw(window)
    next_text.draw(window)

    # Create the "Hold" space:
    hold_box = gr.Rectangle(gr.Point(215, 200), gr.Point(295, 280))
    hold_box.setFill("#7A7A7A")
    hold_text = gr.Text(gr.Point(255, 210), "HOLD")
    hold_text.setTextColor("white")
    hold_text.setStyle("italic")
    hold_box.draw(window)
    hold_text.draw(window)

def drawInstructions(window, play_field):
    '''Draw instructional text, rules for game, and waits for user to push key to start 
    INPUT
    window (gr.GraphWin) - the graphics window in use
    play_field (PlayGrid) - the main PlayGrid object in use'''

    big_pause_box = gr.Rectangle(gr.Point(30, 30), gr.Point(770, 770))
    big_pause_box.setFill("lightgreen")
    big_pause_box.draw(window)

    controls = "Controls:\n"
    controls += "\nA/D - Move Left/Right"
    controls += "\nS - Soft drop down"
    controls += "\nW - Hard drop down (instant)"
    controls += "\nLeft Arrow/N - Rotate counterclockwise"
    controls += "\nRight Arrow/M - Rotate clockwise"
    controls += "\nE - Hold piece"
    control_text = gr.Text(gr.Point(400, 600), controls)
    control_text.draw(window)

    description = "How to play:"
    description += "\nThe blocks are falling!"
    description += "\nUse WASD and the arrow keys"
    description += "\nto rotate and move the falling pieces,"
    description += "\nilling rows, clearing lines, and scoring points!"
    description += "\nHow many lines can you clear?"
    desc_text = gr.Text(gr.Point(400, 200), description)
    desc_text.draw(window)

    title = gr.Text(gr.Point(400, 400), "Quadtris")
    title.setStyle("italic")
    title.setSize(36)
    title.setTextColor("white")
    title.draw(window)

    push_start = gr.Text(gr.Point(400, 440), "Push any key to start/resume!\nPress Q to quit")
    push_start.draw(window)    
    # Undraw everything when user pushes button
    input = window.getKey()
    if input.lower() == "q":
        play_field.gameOver()
    push_start.undraw()
    desc_text.undraw()
    big_pause_box.undraw()
    control_text.undraw()
    title.undraw()

def processInput(input, piece, play_field, window):
    ''' Takes user input as a string and responds appropriately
    Returns the piece
    INPUT
    input (Str) - user input on keyboard
    piece (Quadromino) - the current active piece in play
    play_field (PlayGrid) - the main PlayGrid being used for the game
    window (gr.GraphWin) - the graphics window in use
    
    OUTPUT
    piece (Quadromino) - an updated version of the piece in play'''
    if input == "w":
        piece.hardDrop(play_field)
        play_field.clearLines(window)
        piece = useNextQuadromino(window, play_field)
    elif input == "a":
        piece.move(-1, 0, play_field)
    elif input == "s":
        piece.move(0, 1, play_field)
    elif input == "d":
        piece.move(1, 0, play_field)
    # Left/Right for movement
    elif input == "Right" or input == "m":
        piece.rotate(1, play_field)
    elif input == "Left" or input == "n":
        piece.rotate(-1, play_field)
    elif input == "e":
        piece = play_field.holdQuadromino(piece, window)
    elif input == "Escape":
        drawInstructions(window, play_field)

    return piece

def useNextQuadromino(window, play_field):
    '''Draws and updates the next piece to be used
    INPUT
    window (gr.GraphWin) - the graphics window in use
    play_field (PlayGrid) - the game's PlayGrid
    
    OUTPUT
    piece (Quadromino) - the next piece to be used in active play '''
    piece = play_field.getNextQuadromino(window)
    piece.draw(window)
    return piece

def fallPiece(piece, play_field, lock_length, lock_time):
    ''' Make piece fall / deposit piece if it has collided at the bottom
    INPUT
    piece (Quadromino): the active Quadromino object
    play_field (PlayGrid): the current grid in use
    lock_length (float): How mamy seconds the piece has before it locks after landing
    lock_time (float): a variable used to allow the player some movement before the 
                    piece deposits after colliding. The time the piece should lock.
                    
    OUTPUT:
    lock_time (float): the updated lock_time '''
    # If the piece can fall, lower it by a block and reset lock_stage
    if piece.checkMove(0, 1, play_field):
        piece.move(0, 1, play_field)
        lock_time = time.time() + lock_length

    return lock_time
    
def updateStats(score_txt, lines_txt, lvl_txt, score, lines, level):
    ''' Updates the score, nummber of lines cleared, and level on the GUI
    INPUT
    x_txt vairables should be (gr.Text) objects to display information
    other variables should be (int)s that contain the information to display'''
    score_txt.setText("SCORE: " + str(score))
    lines_txt.setText("Lines\t    \nCleared: " + str(lines))
    lvl_txt.setText("LVL: " + str(level))

def main():
    # Tuple of tuples with (level, cycle_length, line_req) variables
    # level: which level the player is on
    # cycle length: how many frames per cycle/gravity fall
    # line req: how many lines must be cleared to advance to this level
    level_guide = ( (1, 60, 0), 
                    (2, 50, 10), 
                    (3, 40, 20), 
                    (4, 30, 30), 
                    (5, 25, 40), 
                    (6, 20, 50),
                    (7, 15, 60), 
                    (8, 10, 70), 
                    (9, 5, 80), 
                    (10, 3, 90),
                    (11, 2, 100),
                    (12, 1, 110) )

    # Cycle variable to update on a timer (used for auto-falling)
    cycle_stage = 1
    level = 1
    cycle_length = level_guide[level - 1][1]

    # Lock variable to allow for player movement after piece hit ground for a while
    lock_time = 0       # The time the piece will lock (updates after each fall)
    lock_length = 0.5    # How many seconds the player has from the piece landing to its lock time

    # Create a 10 x 20 grid, a window, a play field, and Quadrominos
    win = gr.GraphWin("Quadtris (esc to pause)", 800, 800, autoflush = False)
    play_field = PlayGrid(10, 20)
    play_field.replenishQuadrominos()
    
    # Draw and create GUI visuals
    drawGradient(win, 0, 255, 102)   
    drawPlayField(win)
    play_field.showUpNext(win)
    level_txt = gr.Text(gr.Point(535, 555), "LVL: " + str(level))
    level_txt.draw(win)
    num_line_txt = gr.Text(gr.Point(555, 585), "Lines\t    \nCleared: 0")
    num_line_txt.draw(win)
    score_txt = gr.Text(gr.Point(400, 620), "SCORE: 0")
    score_txt.draw(win)

    # Draw title/pause screen, then play game!
    drawInstructions(win, play_field)
    piece = useNextQuadromino(win, play_field)

    # Get key press
    keyIn = win.checkKey()
    # Until the game if over, respond appropriately to user input, update window, and get new input
    while play_field.gameActive():
        piece = processInput(keyIn, piece, play_field, win)

        # Update ghost projection and cycle count
        piece.projectGhost(play_field)
        

        # action at end of cycle
        if cycle_stage > cycle_length:
            cycle_stage = 1
            # Gravity / locking the piece in place
            lock_time = fallPiece(piece, play_field, lock_length, lock_time)
            # If the lock time has been reached, deposit the piece
            if time.time() >= lock_time:
                piece.depositQuadromino(play_field)
                play_field.clearLines(win)
                piece = useNextQuadromino(win, play_field)

            # Increase level / speed at different increments of line clears, based on the level_guide
            num_lines = play_field.getNumLines()
            if level < len(level_guide):
                line_req = level_guide[level][2]
                if num_lines >= line_req:
                    cycle_length = level_guide[level][1]
                    level = level_guide[level][0]
            # Update GUI/Text
            updateStats(score_txt, num_line_txt, level_txt, play_field.getScore(), num_lines, level)
        
        # Update input, window, and cycle
        cycle_stage += 1
        win.update()
        time.sleep(0.016)   # Roughly 60fps maximum
        keyIn = win.checkKey()

    # Game is now over. Display results and clear board
    piece.undraw()
    time.sleep(0.25)
    gg_txt = gr.Text(gr.Point(400, 100), f"GAME OVER\nScore: {play_field.getScore()}\nClick to close window.")
    gg_txt.setSize(20)
    gg_txt.draw(win)

    for i in range(20):
        play_field.clearRow(19)
        time.sleep(0.1)
        win.update()

    keyIn = win.getMouse()

if __name__ == "__main__":
    main()
