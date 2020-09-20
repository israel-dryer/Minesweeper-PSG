# Minesweeper-PSG
 A minesweeper game built using PySimpleGUI that allows you to add your own custom backgrounds to the tiles.

## Gameplay
Identify all mines on the board by marking with a flag and uncovering all tiles that do not contain mines. If you uncover all tiles that are not mines without uncovering a mine - you win.

#### Uncovering a tile
Left-click on a tile to uncover it.
- **Numbers**: a number tile indicates the count of mines surrounding the tile
- **Mines**: if you reveal a mine tile, the game is over.

#### Marking flags
Right-click on a tile to mark it with a flag; right-click again to remove the flag.

## Difficulty
You can adjust the game difficulty be increasing or decreasing the mine density with the slider. You can adjust the density from 20 to 100 in increments of 10. By default the game will start with 30 mines. If you change the difficulty, you must click the \[RESET\] button to reset the game.

## Changing the image
You can add a custom image to the game board by clicking the \[NEW IMAGE\] button. You can use a PNG or JPG file. The program will attempt to square and crop the image after centering it horizontally. For best results, use an image that is already squared. The program will automatically scale it to fit the gameboard.

<span>
<img src="https://github.com/israel-dryer/Minesweeper-PSG/blob/master/examples/example1.png" width="400" />
<img src="https://github.com/israel-dryer/Minesweeper-PSG/blob/master/examples/example2.png" width="400" />
<img src="https://github.com/israel-dryer/Minesweeper-PSG/blob/master/examples/example4.png" width="400" />
<img src="https://github.com/israel-dryer/Minesweeper-PSG/blob/master/examples/example5.png" width="400" />
 </span>
