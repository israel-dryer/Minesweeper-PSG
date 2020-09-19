from PIL import Image
from math import floor
from random import sample
from time import perf_counter
import pathlib
import PySimpleGUI as sg
import numpy as np

ICONS = {
    'clear': 'images/icons/clear.png',
    'mine16': 'images/icons/naval_mine_25px.png',
    'mine30': 'images/icons/naval_mine_30px.png',
    'timer': 'images/icons/stopwatch_25px.png',
    'clear': 'images/icons/clear.png',
    'flag': 'images/icons/flag_filled_30px.png',
    1: 'images/digits/tile_1.png',
    2: 'images/digits/tile_2.png',
    3: 'images/digits/tile_3.png',
    4: 'images/digits/tile_4.png',
    5: 'images/digits/tile_5.png',
    6: 'images/digits/tile_6.png',
    7: 'images/digits/tile_7.png',
    8: 'images/digits/tile_8.png'    
}


class Game:
    """A Minesweeper game"""
    def __init__(self):
        
        # gameplay variables
        self.flag_count = 0
        self.mine_count = 30
        self.game_over = False
        self.game_started = False
        self.game_timer_start = 0
        self.tile_array = np.array([], dtype='object')
        self.mine_tiles = []
        self.tiles_checked = []
        self.tk_tile_lookup = {}

        # ---- info bar --------------------------------------------------------------------------

        # game timer
        self.game_timer_img = sg.Image(filename=ICONS['timer'])
        self.game_timer_txt = sg.Text('000', font=('TkFixedFont', -14, 'bold'))
        
        # mine counter
        self.mine_counter_img = sg.Image(filename=ICONS['mine16'])
        self.mine_counter_txt = sg.Text(f'{self.mine_count:0>3}', font=('TkFixedFont', -14, 'bold'))
        
        # mine density (diffulty)
        self.mine_density = sg.Slider(range=(20, 100), default_value=self.mine_count, orientation='h', resolution=10,
            disable_number_display=True, enable_events=True, key='-DENSITY-')
        
        # reset game button
        self.reset_btn = sg.Button('Reset', key='-RESET-', size=(9, 1), font=('TkFixedFont', -14))

        # select new image button
        self.img_browse_btn = sg.Button('New Image', size=(9, 1), font=('TkFixedFont', -14), key='-NEWIMAGE-')

        # infobar layout
        infobar_layout = [
            self.game_timer_img, self.game_timer_txt, self.mine_counter_img, self.mine_counter_txt,
            self.mine_density, self.reset_btn, self.img_browse_btn]

        self.infobar = sg.Column([infobar_layout])

        # ---- tile grid -------------------------------------------------------------------------

        self.fg_images = pathlib.Path('images/foreground').iterdir()
        self.grid = None
        self.setup_tile_grid()

        # ---- window ----------------------------------------------------------------------------
        
        window_layout = [[self.infobar], [self.grid]] 
        self.window = sg.Window('Minesweeper', window_layout, finalize=True)

        # tile adjustments and create lookup -----------------------------------------------------
        self.infobar.expand(expand_x=True)
        self.infobar.set_focus()

        for t in self.tile_array.flatten():
            # adjust tile styling
            t.Widget.config(overrelief='flat')

            # set right-click binding
            t.Widget.bind('<Button-3>', lambda e: self.toggle_flag(e))

            # add tile to Tk to PSG lookup
            tk_widget = t.Widget
            self.tk_tile_lookup[tk_widget] = t        

    # ---- methods for setting up the tile grid --------------------------------------------------
    
    def setup_tile_grid(self):
        """ Setup tile grid array and TkWidget lookup """
        grid_layout = []
        for r in range(16):
            row = []
            for c in range(16):
                img = next(self.fg_images)
                t = Tile(img, r, c)
                # add to tile array
                self.tile_array = np.append(self.tile_array, t)
                # add to layout row
                row.append(t)
            grid_layout.append(row)
        self.grid = sg.Column(grid_layout)

        # reshape tile array to grid size
        self.tile_array = self.tile_array.reshape([16, 16])

    def generate_mines(self, first_tile):
        """Set random tiles as mines, excluding the first tile clicked"""
        population = self.tile_array.flatten().tolist()
        population.remove(first_tile)
        self.mine_tiles = sample(population, k=self.mine_count)

        # set mine flag
        for m_tile in self.mine_tiles:
            m_tile.is_mine = True

    def assign_neighbor_properties(self):
        """Assign tile and neighbor properties to each tile"""
        for target_tile in self.tile_array.flatten():
            neighbors, mines = self.find_tile_neighbors(target_tile)
            target_tile.tile_neighbors = neighbors
            target_tile.mine_neighbors = mines

    def find_tile_neighbors(self, target_tile):
        """Find and return neighbors; mine and non-mine neighbors as separate lists"""
        neighbors = []  # this is the 8-block area surrounding the target tile"""
        offsets = np.array([(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)])
        
        for offset in offsets:
            try:
                if all(list(map(lambda x: x >= 0, tuple(offset + target_tile.index)))):
                    neighbors.append(self.tile_array[tuple(target_tile.index + offset)])
            # any index that is out of bounds (negative) or (index error)
            except IndexError:
                continue
        
        # count of neighbors that are mines
        mines = sum(map(lambda x: x.is_mine, neighbors))
        
        return neighbors, mines

    # -- infobar update methods -------------------------------------------------------------------

    def update_game_timer(self):
        """Increment the game timer"""
        if not self.game_started or self.game_over:
            return

        # initialize timer
        if self.game_timer_start == 0:
            self.game_timer_start = perf_counter()
        
        # elapsed time
        elapsed = floor(perf_counter() - self.game_timer_start)

        # adjust timer text
        self.game_timer_txt.update(f'{elapsed:0>3}')

    def update_mine_counter(self):
        """Update the mine counter text"""
        remaining = self.mine_count - self.flag_count
        self.mine_counter_txt.update(f'{remaining:0>3}')

    # ---- button callbacks ----------------------------------------------------------------------

    def set_mine_density(self, window_values):
        """Adjust the mine density based on slider value"""
        self.mine_count = int(window_values['-DENSITY-'])
        self.mine_counter_txt.update(f'{self.mine_count:0>3}')
        self.game_over = True

    def reset_game(self):
        """Reset the gameboard for a ne
        w round"""
        self.tiles_checked.clear()
        self.game_over = False
        self.game_started = False
        self.game_timer_start = 0
        self.game_timer_txt.update('000')
        self.flag_count = 0
        self.update_mine_counter()
        
        for tile in self.tile_array.flatten():
            tile.update(image_filename=tile.image_tile, button_color=sg.theme_button_color())
            tile.Widget.config(relief='raised', overrelief='flat')
            tile.is_flag = False
            tile.is_mine = False
            tile.is_visible = False

    def toggle_flag(self, tk_event):
        """Callback for right-click event"""
        tk_tile = tk_event.widget
        tile = self.tk_tile_lookup.get(tk_tile)

        # tile is already visible or game over
        if any([tile.is_visible, self.game_over]):
            return

        if not tile.image_flag:
            # create the merged image if not existing
            tile.merge_flag_image()

        if tile.is_flag:
            # remove flag image
            tile.is_flag = False
            tile.update(image_filename=tile.image_tile)
            self.flag_count -= 1
            self.update_mine_counter()
        else:
            # add flag image
            tile.is_flag = True
            tile.update(image_filename=tile.image_flag)
            self.flag_count += 1
            self.update_mine_counter()

    def uncover_tiles(self, tile):
        """Uncover tiles that are clicked or near a clicked tile"""
        if any([tile.is_visible, self.game_over, tile.is_flag, tile in self.tiles_checked]):
            return

        # add to list of checked tiles
        self.tiles_checked.append(tile)

        # tile is a mine
        if tile.is_mine:
            tile.update(image_filename=ICONS['mine30'], button_color=('white', 'lightgray'))
            tile.Widget.config(relief='sunken', overrelief='')
            tile.is_visible = True
            self.game_over = True
            self.reveal_mines()
            self.you_lose()

        # tile is a regular tile
        elif tile.mine_neighbors == 0:
            tile.update(image_filename=ICONS['clear'], button_color=('white', 'lightgray'))
            tile.Widget.config(relief='sunken', overrelief='')
            tile.is_visible = True

            # check all neighbors
            for next_tile in tile.tile_neighbors:
                self.uncover_tiles(next_tile)

        # tile has mine neighbors
        else:
            img = ICONS[tile.mine_neighbors]
            tile.update(image_filename=img, button_color=('white', 'lightgray'))
            tile.Widget.config(relief='sunken', overrelief='')
            tile.is_visible = True
            return

    def reveal_mines(self):
        """Reveal all mines; marking correct and incorrect guesses"""
        for mine in self.mine_tiles:
            if mine.is_flag:
                mine.update(image_filename=ICONS['mine30'], button_color=('black', 'green'))
                mine.Widget.config(relief='sunken', overrelief='')
                mine.is_visible = True
            else:
                mine.update(image_filename=ICONS['mine30'], button_color=('black', 'red'))
                mine.Widget.config(relief='sunken', overrelief='')
                mine.is_visible = True

    def new_image(self):
        """Get a new image for the gameboard"""
        source_file = sg.PopupGetFile('Select a gameboard image', file_types=[('Image Files', '*.jpg;*.jpeg;*.jfif;*.jpe;*.png')])
        if source_file:
            dest_folder = 'images/foreground/'
            file_name = 'fg'
            slice_images(source_file, file_name, dest_folder)
            sg.popup_quick_message('Preparing new image...')
        
        # close the existing program and start another
        self.close()
        play()

    # -- other class methods ---------------------------------------------------------------------

    def start_game(self, tile):
        """Check for initial game click, then generate tile neighbors and mines"""
        self.game_started = True
        self.generate_mines(tile)
        self.assign_neighbor_properties()
        self.uncover_tiles(tile)
    
    def check_for_winner(self):
        """Check to see if all mines are accounted for and tiles are uncovered"""
        target = 256 - self.mine_count
        if not self.game_over and len(self.tiles_checked) == target:
            self.game_over = True
            self.you_win()

    def close(self):
        """End the game by closing the application window"""
        self.window.close()

    def you_win(self):
        """Popup to announce game winner"""
        response = sg.popup_yes_no('YOU WIN!!! Would you like to play again?', title='Winner!!')
        if response == 'Yes':
            self.reset_game()
        else:
            sg.PopupQuickMessage("Goodbye!")
            self.close()

    def you_lose(self):
        """Popup to announce game loser"""
        response = sg.popup_yes_no('YOU LOSE!! Would you like to play again?', title='Loser!!')
        if response == 'Yes':
            self.reset_game()
        else:
            sg.PopupQuickMessage("Goodbye!")
            self.close()

class Tile(sg.Button):
    """A game tile"""
    def __init__(self, image, row, col):
        super().__init__(image_filename=image, pad=(0, 0), key=f'tileR{row}C{col}')
        self.temp_file = f'images/temp/tileR{row}C{col}.png'
        self.image_tile = image
        self.image_flag = None
        self.index = np.array([row, col])
        self.is_mine = False
        self.is_visible = False
        self.is_flag = False
        self.tile_neighbors = []  # list of nearby tiles
        self.mine_neighbors = 0  # count of nearby mines

    def merge_flag_image(self):
        """Merge the flag to the image tile on demand"""
        tile = Image.open(self.image_tile)
        flag = Image.open(ICONS['flag'])
        tile.paste(flag, (0, 0), flag)
        tile.save(self.temp_file)
        self.image_flag = self.temp_file


def play():
    """Create and run the game"""
    sg.change_look_and_feel('darkteal12')
    game = Game()

    while True:
        event, values = game.window.read(500)
        if event is None:
            game.window.close()
            break

        if event == '-RESET-':
            game.reset_game()

        if event == '-DENSITY-':
            game.set_mine_density(values)

        if event == '-NEWIMAGE-':
            game.new_image()

        if event.startswith('tile'):
            selected_tile = game.window[event]
            
            if game.game_over and not game.game_started:
                sg.PopupQuickMessage("Click RESET to begin!")
            elif not game.game_started:
                game.start_game(selected_tile)
            else:
                game.uncover_tiles(selected_tile)

            game.check_for_winner()

        game.update_game_timer()


def slice_images(source_image, dest_prefix, folder):
    """Transform image into slices for Minesweeper board and save to local drive"""
    im = Image.open(source_image)

    # crop the image the largest dimensions that a square will allow (left, top, right, bottom)
    x = y = min(im.size)
    squared = im.crop([0, 0, x, y])

    # resize the image to 480 x 480
    resized = squared.resize([480, 480])

    # crop the image to 900 x 480, which is the max size of the gameboard (16 x 30 blocks x 30 pixels)
    to_slice = resized.crop([0, 0, 480, 480])

    # slice the image into squares of 30 x 30 pixels
    file_cnt = 1
    for row in range(16):
        y1 = row * 30
        y2 = row * 30 + 30

        for col in range(16):
            x1 = col * 30
            x2 = col * 30 + 30

            bbox = (x1, y1, x2, y2)
            # slice the new image
            im_slice = to_slice.crop(bbox)

            # save the new file
            filename = f'{folder}/{dest_prefix}_{file_cnt:0>3}.png'
            im_slice.save(filename)
            file_cnt += 1

                   

if __name__ == '__main__':

    # start the program
    play()


