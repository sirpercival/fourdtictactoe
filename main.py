import numpy as np
from functools import partial
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder

def neighbors(point = (0,0,0,0), val = 1, board = np.zeros((5,5,5,5), dtype=np.int)):
    '''return a list of nonzero element coordinates for the moore 
        neighborhood of the center point (chebyshev distance = 1), 
        given a board array'''
    
    dims = board.shape
    assert len(point) == 4 and len(dims) == 4, "Wrong dimensions for center or board"
    radius = [-1, 0, 1]
    neighborhood = []
    
    
    for i in radius:
        if (point[0] + i < 0 or point[0] + i > dims[0] - 1): continue
        for j in radius:
            if (point[1] + j < 0 or point[1] + j > dims[1] - 1): continue
            for k in radius:
                if (point[2] + k < 0 or point[2] + k > dims[2] - 1): continue
                for l in radius:
                    if (point[3] + l < 0 or point[3] + l > dims[3] - 1): continue
                    shft = (i, j, k, l)
                    x, y, z, w = [point[x] + shft[x] for x in range(4)]
                    if board[x, y, z, w] == val and shft != (0, 0, 0, 0):
                        neighborhood.append((x, y, z, w))

    return neighborhood

def check_point(move = (0, 0, 0, 0), p1 = (0, 0, 0, 0), p2 = (1, 1, 1, 1)):
    '''check to see if move lies on the line between point1 and point2'''
    d = None
    each_coord = [False] * 4
    for x in range(4):
        if p2[x] == p1[x]:
            each_coord[x] = move[x] == p1[x]
        elif d is not None:
            each_coord[x] = (move[x] - p1[x]) / (p2[x] - p1[x]) == d
        else:
            d = (move[x] - p1[x]) / (p2[x] - p1[x])
            each_coord[x] = True
    return all(each_coord)

def check_moves(moves = [], p1 = (0, 0, 0, 0), p2 = (1, 1, 1, 1)):
    '''check a bunch of moves against a single line'''
    line = partial(check_point, p1 = p1, p2 = p2)
    check_line = map(line, moves)
    return len([x for x in check_line if x]) == 5

def check_win(move = (0, 0, 0, 0), player = 1, moves = [], board = np.zeros((5,5,5,5), dtype=np.int)):
    '''handle the entire win condition process'''
    if not moves:
        moves.append(move)
        return False
    moves.append(move)
    populated = neighbors(point = move, val = player, board = board)
    for point in populated:
        if check_moves(moves, move, point):
            return True
    return False

Builder.load_string('''

<TicTacToeGrid>:
    cols: 29  # Number of columns
<GridEntry>:
    font_size: self.height
<Interface>:
    orientation: 'vertical'
    # We add child widgets in kv by simply writing another
    # layer in the widget tree, nested as deep as we like
    AnchorLayout:
        TicTacToeGrid:
            id: board
            size: min(self.parent.size), min(self.parent.size)
            size_hint: None, None
    Label:
        size_hint_y: None
        height: sp(40)
        text: 
            '{} to play'.format({-1: 'O', 1: 'X'}[board.current_player])
    Button:
        size_hint_y: None
        height: sp(40)
        text: 'reset'
        on_press: board.reset()
        
''')



class GridEntry(Button):
        coords = ListProperty([0, 0, 0, 0])

class TicTacToeGrid(GridLayout):
    board = ObjectProperty(np.zeros((5,5,5,5), dtype=np.int))
    current_player = NumericProperty(1)
    move_list = DictProperty({1:[], -1:[]})

    def __init__(self, *args, **kwargs):
        super(TicTacToeGrid, self).__init__(*args, **kwargs)
        for x in range(5):
            for y in range(5):
                for z in range(5):
                    for w in range(5):
                        grid_entry = GridEntry(coords=(x, y, z, w))
                        grid_entry.bind(on_release=self.button_pressed)
                        self.add_widget(grid_entry)
                    if z != 4:
                        self.add_widget(Widget())
            if x != 4:
                for i in xrange(29):
                    self.add_widget(Widget())

    def button_pressed(self, button):
        player = {1: 'X', -1: 'O'}
        colours = {1: (0, 1, 0, 1), -1: (1, 0, 0, 1)}

        x, y, z, w = button.coords
        already_played = self.board[x, y, z, w] != 0

        if not already_played:
            self.board[x, y, z, w] = self.current_player
            button.text = player[self.current_player]
            button.background_color = colours[self.current_player]
            winner = None
            if check_win(move = button.coords, player = self.current_player, \
                        moves = self.move_list[self.current_player], \
                        board = self.board):
                winner = '{0} wins!'.format(player[self.current_player])
            elif 0 not in self.board:
                winner = 'Draw... nobody wins!'
            if winner:
                popup = ModalView(size_hint=(0.75, 0.5))
                victory_label = Label(text=winner, font_size=50)
                popup.add_widget(victory_label)
                popup.bind(on_dismiss=self.reset)
                popup.open()
            else:
                self.current_player *= -1

    def reset(self, *args):
        self.board[...] = 0
        self.move_list = {1:[], -1:[]}

        for child in self.children:
            child.text = ''
            child.background_color = (1, 1, 1, 1)

        self.current_player = 1

class Interface(BoxLayout):
    pass


class TicTacToeApp(App):
    
    def build(self):
        self.title = '4D Tic Tac Toe'
        self.icon = '4dtic.png'
        return Interface()

if __name__ == "__main__":
    TicTacToeApp().run()



