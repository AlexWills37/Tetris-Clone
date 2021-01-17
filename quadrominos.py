# Alex Wills
# 18 Nov 2020
# quadrominos.py
#  -a set of classes to play a game of Quatis/Tetris. Contains several different shaped
#   Quadrominos, which each have their own methods of rotation and initialization
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


class Block():
    ''' Blocks take up spaces in the play grid and have collision '''

    def __init__(self, init_col, init_row, color):
        self.col = init_col
        self.row = init_row
        # Each block is a 20 x 20 pixel rectangle
        point1 = gr.Point(300 + self.col * 20, 200 + self.row * 20)
        point2 = gr.Point(point1.getX() + 20, point1.getY() + 20)

        self.square = gr.Rectangle(point1, point2)
        self.square.setFill(color)

    def getColPos(self):
        ''' Returns the x position / column number on the grid '''
        return self.col
    
    def getRowPos(self):
        ''' Returns the y position / row number on the grid '''
        return self.row

    def getSquare(self):
        ''' Returns the main graphics.Rectangle object of the Block object '''
        return self.square

    def setColor(self, color):
        ''' Changes the color of the block '''
        self.square.setFill(color)

    def draw(self, win):
        ''' Draws the Block to the window '''
        self.square.draw(win)

    def undraw(self):
        self.square.undraw()
    
    def move(self, dx, dy):
        ''' Moves piece dx and dy units (each unit is 20 pixels / 1 grid space) '''
        self.col += dx
        self.row += dy
        self.square.move(20 * dx, 20 * dy)

class Quadromino():
    ''' A Quadromino is made of four Blocks that can move and rotate.
    This class is a template. Specific Quadromino classes need to implement the rotate and canRotate functions
    and initialize locations of Blocks differently '''
    def __init__(self):
        # Initialize ghost piece (projected landing spot)
        self.ghost1 = Block(3, 0, "lightgrey")
        self.ghost2 = Block(3, 0, "lightgrey")
        self.ghost3 = Block(3, 0, "lightgrey")
        self.ghost4 = Block(3, 0, "lightgrey")
        self.ghosts = [self.ghost1, self.ghost2, self.ghost3, self.ghost4]    
        self.mini_squares = []

        self.orientation = 1 # Used for proper rotation
        self.can_hold = True    # Every piece can only be held once

        # Attributes from child classes
        #self.squares = [self.square1, ... self.square4]
        #self.color = "color"
  
    def draw(self, win):
        ''' Draws the piece to the screen '''
        for ghost in self.ghosts:
            ghost.draw(win)
        for block in self.squares:
            block.draw(win)

    def undraw(self):
        ''' Undraws the piece and its ghost '''
        for ghost in self.ghosts:
            ghost.undraw()
        for block in self.squares:
            block.undraw()
            
    def checkMove(self, dx, dy, grid):
        ''' Returns true if piece can move dx dy units on the grid '''

        canMove = True
        for block in self.squares:
            # Skip checking if movement is not possible
            if canMove:
                # Get the projected landing spot
                col = block.getColPos() + dx
                row = block.getRowPos() + dy
                
                # If projected space is occupied or out of bounds
                if grid.spaceOccupied(col, row):
                    canMove = False

        return canMove 
     
    def move(self, dx, dy, grid):
        ''' Move the entire piece dx, dy units / grid spaces (20 pixels) 
        grid (PlayGrid) is the current PlayGrid for the game'''

        # If projected space is not occupied, move block:
        if self.checkMove(dx, dy, grid):
            for block in self.squares:
                block.move(dx, dy)
        
    def hardDrop(self, grid):
        ''' Drops piece as far as it will go and deposits it in place '''
        # Calls move down method enough times to collide
        for i in range(21):
            self.move(0, 1, grid)
        # Deposits blocks
        self.depositQuadromino(grid) 

    def canRotate(self, grid):
        ''' Returns true if piece can rotate '''
        pass
        
    def rotate(self, direction, grid):
        ''' Rotates the piece in the direction specified. 
        direction = +1 for clockwise
        direction = -1 for counterclockwise '''
        pass

    def depositQuadromino(self, grid):
        ''' Places Quadromino onto the PlayGrid '''
        # Places Blocks
        for block in self.squares:
            grid.setSpace(block)

        # Undraws ghost blocks
        for ghost in self.ghosts:
            ghost.undraw()

    def calcGhostMove(self, grid):
        ''' Returns the number of spaces a ghost projection can move down '''

        num_moves = 0

        canMove = True

        # Increase num_moves until there is a collision
        while canMove:
            for ghost in self.ghosts:
                # Get projected location
                row = ghost.getRowPos() + num_moves + 1
                col = ghost.getColPos()

                # If out of bounds or space occupied, set canMove to false
                if grid.spaceOccupied(col, row):
                    canMove = False
            # If movement still possible, do another movement
            if canMove:
                num_moves += 1
        return num_moves

    def projectGhost(self, grid):
        ''' Projects the landing location of the Quadromino '''
        # Match ghost with actual piece
        for idx in range(4):
            ghost_x = self.ghosts[idx].getColPos()
            ghost_y = self.ghosts[idx].getRowPos()
            target_x = self.squares[idx].getColPos()
            target_y = self.squares[idx].getRowPos()
            self.ghosts[idx].move(target_x - ghost_x, target_y - ghost_y)

        # Move ghost piece as far as it is projected
        num_moves = self.calcGhostMove(grid)
        for i in range(num_moves):
            for ghost in self.ghosts:
                ghost.move(0, 1)

    def drawMiniIcon(self, window, location):
        ''' draws a miniature clone of the piece to use for the up_next icon / hold
        location (int): 0 - draws in the up_next position
                        1 - draws in the hold position  '''
        # Draw smaller versions of each square (scaled x 0.8, with point 1 of the first square as the center)
        anchor_point = self.square1.getSquare().getP1()
        anchor_x = anchor_point.getX()
        anchor_y = anchor_point.getY()
        for square in self.squares:
            # Get Square coordinates
            rectangle = square.getSquare()
            point1 = rectangle.getP1()
            x1 = point1.getX()
            y1 = point1.getY()
            point2 = rectangle.getP2()
            x2 = point2.getX()
            y2 = point2.getY()

            # Scale to the anchor by a factor of 0.8
            x1 = (x1 - anchor_x) * 0.8
            y1 = (y1 - anchor_y) * 0.8
            x2 = (x2 - anchor_x) * 0.8
            y2 = (y2 - anchor_y) * 0.8

            mini_square = gr.Rectangle(gr.Point(x1, y1), gr.Point(x2, y2))
            mini_square.setFill(self.color)
            mini_square.draw(window)
            self.mini_squares.append(mini_square)
        
        # Move the mini piece to the correct location
        dx = 0
        dy = 0
        # offset pieces to center them all
        if type(self) == JQuadromino:
            dx += 32
        elif type(self) == TQuadromino or type(self) == ZQuadromino:
            dy -= 16
        elif type(self) == OQuadromino:
            dx += 8
            dy -= 16
        elif type(self) == IQuadromino:
            dx -= 8
            dy -= 8

        # "Up Next" location
        if location == 0:
            dx += 520
            dy += 245
        # "Hold" location
        elif location == 1:
            dx += 231
            dy += 245
        
        for square in self.mini_squares:
            square.move(dx, dy)
    
    def undrawMini(self):
        ''' Undraws the mini icon, wherever it is '''
        for square in self.mini_squares:
            square.undraw()
   
    def canHold(self):
        ''' Returns true if the piece can be held, and sets can_hold to False '''
        result = self.can_hold
        self.can_hold = False
        return result

    def resetPiece(self, grid):
        ''' Returns piece to its original state and location '''
        # Move to above the grid (to avoid all collision)
        while not (self.square1.getRowPos() < -3):
            for square in self.squares:     # Bypass checkMove to avoid collision with potential pieces above
                square.move(0, -1)

        # Return to upright rotation
        while not (self.orientation == 1):
            self.rotate(1, grid)

        # Move to beginning location (square 1 to (3,0), with exception of J piece to (5,0))
        current_x = self.square1.getColPos()
        current_y = self.square1.getRowPos()
        self.move(3 - current_x, 0 - current_y, grid)
        if type(self) == JQuadromino:
            self.move(2, 0, grid)


# # # # # # # # # # # # # # # # #
# Specific shaped Quadrominos:  #
# - - - - - - - - - - - - - - - # # # # # # # # # # # # # # # # #
# Every Shape has three methods:                                #
#                                                               #
# __init__(self, init_win):                                     #
#       Constructs the Quadromino in the right shape and color  #
#                                                               #
# canRotate(self, direction, grid):                             #
#       Uses self.orientation, direction, and grid to determine #
#       if the piece is able to rotate                          #
#                                                               #
# rotate(self, direction, grid):                                #
#       Uses self.orientation and direction to move the squares #
#       around for rotation, IF canRotate returns true          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class TQuadromino(Quadromino):
    ''' Quadromino that looks like this: [] [] []
                                            []    '''
    def __init__(self):
        
        # Initialize ghost pieces
        super().__init__()
        
        # Initialize piece
        self.color = "purple"
        self.square1 = Block(3, 0, self.color)
        self.square2 = Block(4, 0, self.color)
        self.square3 = Block(4, 1, self.color)
        self.square4 = Block(5, 0, self.color)

        self.squares = [self.square1, self.square2, self.square3, self.square4]

    def rotate(self, direction, grid):
        ''' Rotates the piece in the direction specified. 
        direction = +1 for clockwise
        direction = -1 for counterclockwise '''

        # If rotation is possible, use current orientation and direction
        # to move Blocks to the next orientation
        if self.canRotate(grid):                # Current orientation:
            if self.orientation == 1:           # orientation 1: [1][2][4]  
                if direction > 0:               #                   [3]
                    self.orientation  = 2
                    self.square4.move(-1, -1)
                else:
                    self.orientation = 4
                    self.square1.move(1, 1)
                    self.square3.move(1, -1)
                    self.square4.move(-1, -1)
                                                
            elif self.orientation == 2:         # orientation 2:    [4]
                if direction > 0:               #                [1][2]
                    self.orientation = 3        #                   [3]
                    self.square3.move(1, -1)
                else:
                    self.orientation = 1
                    self.square4.move(1, 1)
                    
            elif self.orientation == 3:         # orientation 3:    [4]
                if direction > 0:               #                [1][2][3]
                    self.orientation = 4 
                    self.square1.move(1, 1)
                else:
                    self.orientation = 2
                    self.square3.move(-1, 1)

            else:
                if direction > 0:               # orientation 4:    [4]
                    self.orientation = 1        #                   [2][3]
                    self.square1.move(-1, -1)   #                   [1]
                    self.square3.move(-1, 1)
                    self.square4.move(1, 1)
                else:
                    self.orientation = 3
                    self.square1.move(-1, -1)


    def canRotate(self, grid):
        ''' Returns true if piece can rotate '''

        # With the T piece, we only check one position:
        #           [X] <-------- The space that a rotation will occupy
        #        [1][2][4]
        #           [3]

        canRotate = True
        # Square 2 is the center Block
        row = self.square2.getRowPos()
        col = self.square2.getColPos()
        # If the target space is occupied or out of bounds, do not rotate
        if self.orientation == 1:
            if grid.spaceOccupied(col, row - 1):
                canRotate = False
        elif self.orientation == 2:
            if grid.spaceOccupied(col + 1, row):
                canRotate = False
        elif self.orientation == 3:
            if grid.spaceOccupied(col, row + 1):
                canRotate = False
        else:
            if grid.spaceOccupied(col - 1, row):
                canRotate = False

        return canRotate

class IQuadromino(Quadromino):
    ''' Quadromino that looks like : [] [] [] [] '''
    def __init__(self):
        # Initialize ghost pieces
        super().__init__()

        self.color = "cyan"
        self.square1 = Block(3, 0, self.color)
        self.square2 = Block(4, 0, self.color)
        self.square3 = Block(5, 0, self.color)
        self.square4 = Block(6, 0, self.color)

        self.squares = [self.square1, self.square2, self.square3, self.square4]

    def rotate(self, direction, grid):
        ''' rotates the piece if it can. 
        direction = +1 for clockwise
        direction = -1 for counterclockwise'''
        

        if(self.canRotate(direction, grid)):
            if self.orientation == 1:            # orientation 1:  [1][2][3][4]
                if direction > 0:
                    self.orientation = 2
                    self.square1.move(2, 2)
                    self.square2.move(1, 1)
                    self.square4.move(-1, -1)
                else:
                    self.orientation = 4
                    self.square1.move(1, -1)
                    self.square3.move(-1, 1)
                    self.square4.move(-2, 2)

            elif self.orientation == 2:         # orientation 2:        [4]
                if direction > 0:               #                       [3]
                    self.orientation = 3        #                       [2]
                    self.square4.move(-2, 2)    #                       [1]
                    self.square3.move(-1, 1)
                    self.square1.move(1, -1)    
                else:
                    self.orientation = 1
                    self.square1.move(-2, -2)
                    self.square2.move(-1, -1)
                    self.square4.move(1, 1)

            elif self.orientation == 3:         # orientation 3:  [4][3][2][1]
                if direction > 0:
                    self.orientation = 4
                    self.square1.move(-2, -2)
                    self.square2.move(-1, -1)
                    self.square4.move(1, 1)
                else:
                    self.orientation = 2
                    self.square1.move(-1, 1)
                    self.square3.move(1, -1)
                    self.square4.move(2, -2)
            
            else:                               # orientation 4:     [1]
                if direction > 0:               #                    [2]
                    self.orientation = 1        #                    [3]
                    self.square1.move(-1, 1)    #                    [4]
                    self.square3.move(1, -1)
                    self.square4.move(2, -2)
                else:
                    self.orientation = 3
                    self.square1.move(2, 2)
                    self.square2.move(1, 1)
                    self.square4.move(-1, -1)        

    def canRotate(self, direction, grid):
        ''' Returns true if the piece can rotate in the given direction on the given grid'''

        # Set one square as the anchor that does not change position (based on orientation/direction)
        # Check the spaces around the anchor, where the other squares will move to. See rotate() for orientation guide

        can_rotate = True
        # locations of spaces to check
        cols = []
        rows = []

        if self.orientation == 1:
            if direction > 0:   # 1 -> 2 anchor: [3]
                # Get locations of target squares
                anchor_row = self.square3.getRowPos()
                cols.append(self.square3.getColPos())
            else:   # 4 <- 1 anchor: [2]
                anchor_row = self.square2.getRowPos()
                cols.append(self.square2.getColPos())
            # One block above, two below
            rows += [anchor_row - 1, anchor_row + 1, anchor_row + 2]
        elif self.orientation == 2:
            if direction > 0:   # 2 -> 3 anchor: [2]
                anchor_col = self.square2.getColPos()
                rows.append(self.square2.getRowPos())
            else:   # 1 <- 2 anchor: [3]
                anchor_col = self.square3.getColPos()
                rows.append(self.square3.getRowPos())
            # One block right, two left
            cols += [anchor_col + 1, anchor_col - 1, anchor_col - 2]
        elif self.orientation == 3:
            if direction > 0:   # 3 -> 4 anchor: [3]
                anchor_row = self.square3.getRowPos()
                cols.append(self.square3.getColPos())
            else:   # 2 <- 3 anchor: [2]
                anchor_row = self.square2.getRowPos()
                cols.append(self.square2.getColPos())
            # One block below, two above
            cols += [anchor_row + 1, anchor_row - 1, anchor_row - 2]
        else:   # orientation = 4
            if direction > 0:   # 4 -> 1 anchor: [2]
                anchor_col = self.square2.getColPos()
                rows.append(self.square2.getRowPos())
            else:   # 3 <- 4 anchor: [3]
                anchor_col = self.square3.getColPos()
                rows.append(self.square3.getRowPos())
            # One block left, two right
            cols += [anchor_col - 1, anchor_col + 1, anchor_col + 2]
        
        # Check all blocks until end is reached or a space is occupied
        for row in rows:
            for col in cols:
                if can_rotate:
                    # Important to ensure space is in-bounds before checking the space
                    can_rotate = not grid.spaceOccupied(col, row)

        # True if all spaces selected are not occupied
        return can_rotate
                
class OQuadromino(Quadromino):
    ''' Quadromino that looks like : [] []
                                     [] [] '''
    def __init__(self):
        super().__init__()

        self.color = "yellow"
        self.square1 = Block(4, 0, self.color)
        self.square2 = Block(5, 0, self.color)
        self.square3 = Block(4, 1, self.color)
        self.square4 = Block(5, 1, self.color)

        self.squares = [self.square1, self.square2, self.square3, self.square4]

class LQuadromino(Quadromino):
    ''' Quadromino that looks like this:    []
                                            []
                                            [] [] '''
    def __init__(self):
        super().__init__()

        self.color = "orange"
        self.square1 = Block(3, 1, self.color)
        self.square2 = Block(4, 1, self.color)
        self.square3 = Block(5, 1, self.color)
        self.square4 = Block(5, 0, self.color)

        self.squares = [self.square1, self.square2, self.square3, self.square4]

    def canRotate(self, direction, grid):
        ''' Returns true if the piece can rotate in the given direction '''
        # Always need to check 2 spaces, so use two booleans. True if empty                      X [4]
        space1 = False      # Space 1, regardless of direction, is the "elbow" of the piece: [1][2][3]
        space2 = False      # Space 2 is dependent on orientation and direction, and is found relative to space 1
        if self.orientation == 1:
            # Find the position of the "elbow" location
            row = self.square2.getRowPos() - 1
            col = self.square2.getColPos()
            space1 = not grid.spaceOccupied(col, row)
            # Find the position of space2
            if direction > 0:   # 1 -> 2
                row += -1
            else:   # 4 <- 1
                row += 2
                col += 1
            space2 = not grid.spaceOccupied(col, row)

        elif self.orientation == 2:
            row = self.square3.getRowPos() - 1
            col = self.square3.getColPos()
            space1 = not grid.spaceOccupied(col, row)
            if direction > 0:   # 2 -> 3
                col += 1
            else:   # 1 <- 2
                row += 1
                col += -2
            space2 = not grid.spaceOccupied(col, row)

        elif self.orientation == 3:
            row = self.square1.getRowPos() + 1
            col = self.square1.getColPos()
            space1 = not grid.spaceOccupied(col, row)
            if direction > 0:   # 3 -> 4
                row += 1
            else:   # 2 <- 3
                row += -2
                col += -1
            space2 = not grid.spaceOccupied(col, row)

        else:
            row = self.square1.getRowPos() + 1
            col = self.square1.getColPos()
            space1 = not grid.spaceOccupied(col, row)
            if direction > 0:   # 4 -> 1
                col += -1
            else:   # 3 <- 4
                row += -1
                col += 2
            space2 = not grid.spaceOccupied(col, row)

        return space1 and space2
            
    def rotate(self, direction, grid):
        ''' Rotates the piece in the direction if possible.
        direction = +1 clockwise
        direction = -1 counterclockwise '''
        if self.canRotate(direction, grid):
            if self.orientation == 1:           # orientation 1:       [4]
                if direction > 0:               #                [1][2][3]
                    self.orientation = 2
                    self.square4.move(-1, 0)
                    self.square1.move(1, -2)
                else:
                    self.orientation = 4
                    self.square2.move(1, 1)
                    self.square1.move(1, -1)
            
            elif self.orientation == 2:         # orientation 2:    [1]
                if direction > 0:               #                   [4]
                    self.orientation = 3        #                   [2][3]
                    self.square1.move(1, 1)
                    self.square3.move(1, -1)
                else:
                    self.orientation = 1
                    self.square1.move(-1, 2)
                    self.square4.move(1, 0)
            
            elif self.orientation == 3:         # orientation 3:    [4][1][3]
                if direction > 0:               #                   [2]
                    self.orientation = 4
                    self.square1.move(-1, 0)
                    self.square2.move(1, 1)
                    self.square3.move(-1, 1)
                    self.square4.move(1, 0)
                else:
                    self.orientation = 2
                    self.square1.move(-1, -1)
                    self.square3.move(-1, 1)

            else:                               # orientation 4:    [1][4]
                if direction > 0:               #                      [3]
                    self.orientation = 1        #                      [2]
                    self.square1.move(-1, 1)
                    self.square2.move(-1, -1)
                else: 
                    self.orientation = 3
                    self.square1.move(1, 0)
                    self.square2.move(-1, -1)
                    self.square3.move(1, -1)
                    self.square4.move(-1, 0)

class JQuadromino(Quadromino):
    ''' Quadromino that looks like this:    []
                                            []
                                         [] [] 
        Mirror of the LQuadromino'''
    def __init__(self):
        super().__init__()

        self.color = "blue"
        self.square1 = Block(5, 1, self.color)
        self.square2 = Block(4, 1, self.color)
        self.square3 = Block(3, 1, self.color)
        self.square4 = Block(3, 0, self.color)

        self.squares = [self.square1, self.square2, self.square3, self.square4]

    def canRotate(self, direction, grid):
        ''' Returns true if the piece is able to rotate in the given direction '''
        # Just like the L piece but with different values.
        # We check space1 in the "elbow" of the piece, and space2 is relative to the "elbow"
        space1 = False
        space2 = False
        if self.orientation == 1:
            row = self.square2.getRowPos() - 1
            col = self.square2.getColPos()
            space1 = not grid.spaceOccupied(col, row)
            if direction > 0:
                row += -1
            else:
                col += -1
                row += 2
            space2 = not grid.spaceOccupied(col, row)
        
        elif self.orientation == 2:
            col = self.square3.getColPos()
            row = self.square3.getRowPos() - 1
            space1 = not grid.spaceOccupied(col, row)
            if direction > 0:
                col += -1
            else:
                col += 2
                row += 1
            space2 = not grid.spaceOccupied(col, row)
        
        elif self.orientation == 3:
            col = self.square1.getColPos()
            row = self.square1.getRowPos() + 1
            space1 = not grid.spaceOccupied(col, row)
            if direction > 0:
                row += 1
            else:
                col += 1
                row += -2
            space2 = not grid.spaceOccupied(col, row)
        
        else:
            col = self.square1.getColPos()
            row = self.square1.getRowPos() + 1
            space1 = not grid.spaceOccupied(col, row)
            if direction > 0:
                col += 1
            else:
                col += -2
                row += -1
            space2 = not grid.spaceOccupied(col, row)

        return space1 and space2



    def rotate(self, direction, grid):
        ''' Rotates the piece in the givn direction if possible.
        direction = +1 clockwise
        direction = -1 counterclockwise '''
        # Note: direction variable is reversed because this method is based off of the LQuadromino
        # Class, which is mirrored. Thus clockwise <-> counterclockwise
        direction = -1 * direction
        if self.canRotate(direction, grid):
            if self.orientation == 1:           # orientation 1:    [4]
                if direction > 0:               #                   [3][2][1]
                    self.orientation = 2
                    self.square1.move(-1, -2)
                    self.square4.move(1, 0)
                else:
                    self.orientation = 4
                    self.square2.move(-1, 1)
                    self.square1.move(-1, -1)

            elif self.orientation == 2:         # orientation 2:       [1]
                if direction > 0:               #                      [4]
                    self.orientation = 3        #                   [3][2]
                    self.square3.move(-1, -1)
                    self.square1.move(-1, 1)
                else:
                    self.orientation = 1
                    self.square1.move(1, 2)
                    self.square4.move(-1, 0)

            elif self.orientation == 3:         # orientation 3: [3][1][4]
                if direction > 0:               #                      [2]
                    self.orientation = 4
                    self.square1.move(1, 0)
                    self.square4.move(-1, 0)
                    self.square2.move(-1, 1)
                    self.square3.move(1, 1)
                else:
                    self.orientation = 2
                    self.square3.move(1, 1)
                    self.square1.move(1, -1)
            
            else:                               # orientation 4:    [4][1]
                if direction > 0:               #                   [3]
                    self.orientation = 1        #                   [2]
                    self.square2.move(1, -1)
                    self.square1.move(1, 1)
                else:
                    self.orientation = 3
                    self.square1.move(-1, 0)
                    self.square4.move(1, 0)
                    self.square2.move(1, -1)
                    self.square3.move(-1, -1)

class SQuadromino(Quadromino):
    ''' Quadromino that looks like this:    [] []
                                         [] []       '''
    def __init__(self):
        super().__init__()

        self.color = "lightgreen"
        self.square1 = Block(3, 1, self.color)
        self.square2 = Block(4, 1, self.color)
        self.square3 = Block(4, 0, self.color)
        self.square4 = Block(5, 0, self.color)

        self.squares = [self.square1, self.square2, self.square3, self.square4]

    def canRotate(self, direction, grid):
        ''' Returns true if the piece is able to rotate in the direction '''
        #|   | A |   |   |
        #|   |[3]|[4]|   |
        #|[1]|[2]| X |   | <--- We always check this corner (like the "elbow" with the other piecees)
        #|   |   | B |   |      And the other space to check is relative to the inner corner

        col1 = 0    # (col1, row1) for the inner corner/space1
        row1 = 0
        col2 = 0    # (col2, row2) for the other space/space2
        row2 = 0    

        # Get the correct spaces
        if self.orientation == 1:
            row1 = self.square4.getRowPos() + 1
            col1 = self.square4.getColPos()
            if direction > 0: # 1 -> 2
                col2 = col1 - 1
                row2 = row1 - 2
            else:   # 1 -> 4
                row2 = row1 + 1
                col2 = col1
        
        elif self.orientation == 2:
            col1 = self.square3.getColPos()
            row1 = self.square3.getRowPos() + 1
            if direction > 0:   # 2 -> 3
                col2 = col1 + 2
                row2 = row1 - 1
            else:   # 2 -> 1
                col2 = col1 -1
                row2 = row1
        
        elif self.orientation == 3:
            col1 = self.square3.getColPos()
            row1 = self.square3.getRowPos() - 1
            if direction > 0:   # 3 -> 4
                col2 = col1 + 1
                row2 = row1 + 2
            else:   # 3 -> 2
                row2 = row1 - 1
                col2 = col1
        
        else:
            col1 = self.square2.getColPos()
            row1 = self.square2.getRowPos() - 1
            if direction > 0:   # 4 -> 1
                col2 = col1 - 2
                row2 = row1 + 1
            else:   # 4 -> 3
                col2 = col1 + 1
                row2 = row1

        # True if both space1 and space2 are not occupied
        return (not grid.spaceOccupied(col1, row1)) and (not grid.spaceOccupied(col2, row2))

    def rotate(self, direction, grid):
        ''' Rotates the piece if it can.
        direction = +1 clockwise
        direction = -1 counterclockwise '''
        if self.canRotate(direction, grid):
            if self.orientation == 1:           # orientation 1:    [3][4]
                if direction > 0:               #                [1][2]
                    self.orientation = 2
                    self.square2.move(1, 0)
                    self.square1.move(1, -2)
                else:
                    self.orientation = 4
                    self.square1.move(2, 1)
                    self.square2.move(1, 0)
                    self.square3.move(0, 1)
                    self.square4.move(-1, 0)
            
            elif self.orientation == 2:         # orientation 2:    [1]
                if direction > 0:               #                   [3][4]
                    self.orientation = 3        #                      [2]
                    self.square3.move(0, 1)
                    self.square1.move(2, 1)
                else:
                    self.orientation = 1
                    self.square2.move(-1, 0)
                    self.square1.move(-1, 2)
            
            elif self.orientation == 3:         # orientation 3:       [4][1]
                if direction > 0:               #                   [3][2]
                    self.orientation = 4
                    self.square4.move(-1, 0)
                    self.square1.move(-1, 2)
                else:
                    self.orientation = 2
                    self.square3.move(0, -1)
                    self.square1.move(-2, -1)
            
            else:
                if direction > 0:               # orientation 4:    [4]
                    self.orientation = 1        #                [3][2]
                    self.square1.move(-2, -1)   #                [1]
                    self.square2.move(-1, 0)
                    self.square3.move(0, -1)
                    self.square4.move(1, 0)
                else:
                    self.orientation = 3
                    self.square4.move(1, 0)
                    self.square1.move(1, -2)
            
class ZQuadromino(Quadromino):
    ''' Quadromino that looks like this:    [] []
                                               [] [] '''
    def __init__(self):
        super().__init__()

        self.color = "red"
        self.square1 = Block(3, 0, self.color)
        self.square2 = Block(4, 0, self.color)
        self.square3 = Block(4, 1, self.color)
        self.square4 = Block(5, 1, self.color)

        self.squares = [self.square1, self.square2, self.square3, self.square4]

    def canRotate(self, direction, grid):
        ''' Returns true if the piece is able to rotate in the direction '''
        #|   |   | A |   |
        #|[1]|[2]| X |   | <--- We always check this corner (like the "elbow" with the other piecees)
        #|   |[3]|[4]|   |      And the other space to check is relative to the inner corner
        #|   | B |   |   |      

        col1 = 0    # (col1, row1) for the inner corner/space1
        row1 = 0
        col2 = 0    # (col2, row2) for the other space/space2
        row2 = 0    
        # Get the correct spaces
        if self.orientation == 1:
            col1 = self.square4.getColPos()
            row1 = self.square4.getRowPos() - 1
            if direction > 0:
                col2 = col1
                row2 = row1 - 1
            else:
                col2 = col1 - 1
                row2 = row1 + 2
        
        elif self.orientation == 2:
            col1 = self.square4.getColPos()
            row1 = self.square4.getRowPos() + 1
            if direction > 0:
                col2 = col1 + 1
                row2 = row1
            else:
                col2 = col1 - 2
                row2 = row1 - 1
        
        elif self.orientation == 3:
            col1 = self.square2.getColPos()
            row1 = self.square2.getRowPos() + 1
            if direction > 0:
                col2 = col1
                row2 = row1 + 1
            else:
                col2 = col1 + 1
                row2 = row1 - 2

        else:
            col1 = self.square2.getColPos()
            row1 = self.square2.getRowPos() - 1
            if direction > 0:
                col2 = col1 - 1
                row2 = row1
            else:
                col2 = col1 + 2
                row2 = row1 + 1

        # True if both (col1, row1) and (col2, row2) are not occupied
        return (not grid.spaceOccupied(col1, row1)) and (not grid.spaceOccupied(col2, row2))

    def rotate(self, direction, grid):
        ''' Rotates the piece if it can.
        direction = +1 clockwise
        direction = -1 counterclockwise '''
        if self.canRotate(direction, grid):
            if self.orientation == 1:           # orientation 1:[1][2]
                if direction > 0:               #                  [3][4]
                    self.orientation = 2
                    self.square4.move(0, -1)
                    self.square1.move(2, -1)
                else:
                    self.orientation = 4
                    self.square1.move(1, 2)
                    self.square2.move(0, 1)
                    self.square3.move(1, 0)
                    self.square4.move(0, -1)

            elif self.orientation == 2:         # orientation 2:      [1]
                if direction > 0:               #                  [2][4]
                    self.orientation = 3        #                  [3]
                    self.square3.move(1, 0)
                    self.square1.move(1, 2)
                else:
                    self.orientation = 1
                    self.square4.move(0, 1)
                    self.square1.move(-2, 1)

            elif self.orientation == 3:         # orientation 3:   [2][4]
                if direction > 0:               #                     [3][1]
                    self.orientation = 4
                    self.square2.move(0, 1)
                    self.square1.move(-2, 1)
                else:
                    self.orientation = 2
                    self.square3.move(-1, 0)
                    self.square1.move(-1, -2)

            else:
                if direction > 0:               # orientation 4:      [4]
                    self.orientation = 1        #                  [2][3]
                    self.square1.move(-1, -2)   #                  [1]
                    self.square2.move(0, -1)
                    self.square3.move(-1, 0)
                    self.square4.move(0, 1)                    
                else:
                    self.orientation = 3
                    self.square2.move(0, -1)
                    self.square1.move(2, -1)
