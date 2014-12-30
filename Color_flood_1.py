import tkinter
import random

information = '''
    Нужно закрасить все клетки одним цветом.
    Клетки заливаются выбранным цветом начиная
    с левого верхнего угла.
    Области с таким же цветом присоединяются.

    Have to fill all the cells of the same color.
    The cells are filled with the selected color
    starting from the upper left corner.
    Area with the same color are connected.
    
    www.github.com/koljutsii
'''

values = {'cell':20, 'top':40, 'down':60, 'indent':30, 
        'col_button_size':40, 'act_button_size':30, 'buttons_position': 'hor', 
        'quest_win':(340,260), 'quest_rect':100, 
        'quest_points':((40,40),(120,120),(200,40)), 'quest_bg':'lightgoldenrod2', 
        'quest_vars':('small', 'medium', 'large'), 
        'quest_colors':('medium purple', 'green3', 'firebrick1'), 
        'small':(12,12,22), 'medium':(18,18,34), 'large':(24,24,44), 
        'colors':('midnight blue', 'medium purple', 'green3', 'red2', 'chocolate1', 'yellow'),
        '_colors':('darkslate blue', 'light slate blue', 'chartreuse3', 'firebrick2', 'chocolate2', 'gold2')}

class Board:
    '''
    Создает ячейки на игральной доске и закрашивает их.
    Creates a cell on the game board and fills them.
    '''
    def __init__(self, canvas, size):
        self.canvas = canvas
        self.width, self.height = values[size][:2]
        st, cl = values['indent'], values['cell']
        self.cells = [[self.canvas.create_rectangle((st+cl*w, st+cl*h, st+cl*(w+1), st+cl*(h+1))) for w in range(self.width)] for h in range(self.height)]
    
    def repaint(self, table):
        for h in range(self.height):
            for w in range(self.width):
                num = table[h][w]
                color = values['colors'][num]
                self.canvas.itemconfig(self.cells[h][w], fill=color, outline=color)
    
class Game:
    '''
    Создает игральную доску, таблицу цветов, ведет учет сделаных ходов.
    Creates a game board, color table, keeps track of the made moves.
    '''
    def __init__(self, canvas, size):
        self.width, self.height = values[size][:2]
        self.canvas = canvas
        self.old_tables = []
        self.moment_table = [[random.randint(0,5) for c in range(self.width)] for r in range(self.height)]
        self.board = Board(canvas, size)
        self.board.repaint(self.moment_table)
        self.count = Count(size)
        self.end_text = 0
        
    def destroy(self):
        '''
        Удаляет все при начале новой игры. Надеюсь, что так игра будет занимать меньше памяти.
        Removes all at the beginning of a new game. I hope that this game will take up less memory.
        '''
        del self.width, self.height, self.old_tables, self.moment_table, self.board, self.count
    
    def make_changes(self, r, c, color, old_color):
        if self.moment_table[r][c] == old_color:
            self.moment_table[r][c] = color
            if r+1 < self.height:
                if self.moment_table[r+1][c] == old_color:
                    self.make_changes(r+1, c, color, old_color)
            if c+1 < self.width:
                if self.moment_table[r][c+1] == old_color: 
                    self.make_changes(r, c+1, color, old_color)
            if r-1 >= 0:
                if self.moment_table[r-1][c] == old_color:
                    self.make_changes(r-1, c, color, old_color)
            if c-1 >= 0:
                if self.moment_table[r][c-1] == old_color: 
                    self.make_changes(r, c-1, color, old_color)
        
    def make_move(self, color):
        if color != self.moment_table[0][0]:
            old_color = self.moment_table[0][0]
            self.old_tables.append(self.copy(self.moment_table))
            self.make_changes(0, 0, color, old_color)
            self.board.repaint(self.moment_table)
            self.count.make('+')
        
    def make_undo(self):
        if len(self.old_tables) > 0:
            self.moment_table = self.copy(self.old_tables[-1])
            del self.old_tables[-1]
            self.board.repaint(self.moment_table)
            self.count.make('-')
            self.make_end('back')
            
    def copy(self, list):
        '''
        Функция копирует массив. Другие варианты делают ссылку, и потому undo не работает.
        Function copies the array. Other methods make links and 'undo' does not work.
        '''
        return [[list[r][c] for c in range(len(list[0]))] for r in range(len(list))]
        
    def make_end(self, back=0):
        if self.end_text:
            self.canvas.itemconfig(self.end_text, state=tkinter.DISABLED)
        else:
            self.end_text = self.canvas.create_text(values['indent'], values['indent'], anchor='nw', font='Arial 20 bold', fill='black', text='The END. New?', state=tkinter.DISABLED)
        if back == 'back':
            self.canvas.itemconfig(self.end_text, state=tkinter.HIDDEN)

class Count:
    '''
    Счетчик ходов.
    Все переменные создаются при создании Game. Место для счетчика указывается после создание холста.
    Counter moves.
    All variables are created when you create a 'Game'. Place for the counter is indicated after the creation of the canvas.
    '''
    def __init__(self, size):
        self.moves = values[size][2]
        self.moment = 0
        self.canvas = 0
        self.count = 0
        
    def get_place(self, canvas, coords):
        self.canvas = canvas
        tx = '{}/{}'.format(self.moment, self.moves)
        self.count = self.canvas.create_text(coords, text=tx, anchor='center', fill='firebrick2', font='Arial 16 bold')
    
    def make(self, point):
        if point == '+':
            self.moment += 1
        elif point == '-':
            self.moment -= 1
        if self.count:
            tx = '{}/{}'.format(self.moment, self.moves)
            self.canvas.itemconfig(self.count, text=tx)
            
    def state(self):
        return self.moves - self.moment 
                    
def make_canvases(win, size):
    '''
    Создает холсты в окне с игрой нужного размера и в правильном расположении.
    Creates canvases in the game window right size and in the right location.
    '''
    width, height, moves_count = values[size]
    top_width = width * values['cell'] + values['indent']*2
    top_height = values['top']
    board_width = width * values['cell'] + values['indent']*2
    board_height = height * values['cell'] + values['indent']*2
    butt_width = width * values['cell'] + values['indent']*2
    butt_height = values['down']
    
    if values['buttons_position'] == 'vert':
        top_width = top_width + values['down']
        butt_width, butt_height = butt_height, butt_width
        
    can_info = tkinter.Canvas(win, width=top_width, height=top_height, highlightthickness=0, bg='grey80')
    can_board = tkinter.Canvas(win, width=board_width, height=board_height, highlightthickness=0, bg='grey94')
    can_buttons = tkinter.Canvas(win, width=butt_width, height=butt_height, highlightthickness=0, bg='grey80')
    
    if values['buttons_position'] == 'hor':
        can_info.pack()
        can_board.pack()
        can_buttons.pack()
    elif values['buttons_position'] == 'vert':
        can_info.pack(side='top')
        can_board.pack(side='left')
        can_buttons.pack(side='right')
        
    return can_info, can_board, can_buttons
        
def make_color_buttons(canvas, i, size):
    but, sp = values['col_button_size'], (values['down']-values['col_button_size'])/2
    st = ((values[size][0] * values['cell'] + values['indent'] * 2) - (but * 6 + sp * 5)) / 2
    color = values['colors'][i]
    if values['buttons_position'] == 'hor':
        coords = (st+but*i+sp*i, sp, st+but*(i+1)+sp*i, sp+but) 
    elif values['buttons_position'] == 'vert':
        coords = (sp, st+but*i+sp*i, sp+but, st+but*(i+1)+sp*i)
    return canvas.create_rectangle(coords, fill=color, outline='black', tag=str(i)) #width=2
    
def make_info_buttons(canvas, size, count_adr):
    width = values[size][0] * values['cell'] + values['indent']*2
    sp, but = (values['top']-values['act_button_size'])/2, values['act_button_size']
    undo_but = canvas.create_rectangle(sp, sp, sp+but*3, sp+but, fill='grey50', outline='grey94', width=2, tag='undo')
    new_but = canvas.create_rectangle(width-sp-but*3, sp, width-sp, sp+but, fill='grey50', outline='grey94', width=2, tag='new')
    
    canvas.create_text(sp+but*3/2, sp+but/2, text='undo', anchor='center', fill='chartreuse3', font='Arial 16 bold', state=tkinter.DISABLED)
    canvas.create_text(width-sp-but*3/2, sp+but/2, text='new', anchor='center', fill='darkslate blue', font='Arial 16 bold', state=tkinter.DISABLED)
    
    count_but = canvas.create_rectangle(width/2-but, sp, width/2+but, sp+but, fill='grey30', outline='grey94', width=2)
    count_adr.get_place(canvas, (width/2, sp+but/2))
    
    return [undo_but, new_but]
    
def choice_window(win):
    '''
    Предоставляет выбор размера поля, расположения панели с кнопками, информацию.
    Provides a variety of field size, the location of the buttons, the information.
    '''
    #win.overrideredirect(True)
    #Поместить окно в центр экрана. Put window in the center of the screen.
    win.geometry('+480+250')
    canvas = tkinter.Canvas(win, width=values['quest_win'][0], height=values['quest_win'][1], highlightthickness=0, bg=values['quest_bg'])
    canvas.pack()
    
    for i in range(3):
        rect, pos, color, var = values['quest_rect'], values['quest_points'][i], values['quest_colors'][i], values['quest_vars'][i]
        tx = '{}x{}'.format(values[var][0], values[var][1])
        canvas.create_rectangle(pos[0], pos[1], pos[0]+rect, pos[1]+rect, tag=var, fill=color, outline='grey25', width=2)
        canvas.create_text(pos[0]+rect/2, pos[1]+rect/2, text=tx, font='Arian 18 bold', fill='black', anchor='center', state=tkinter.DISABLED)
    
    width, height = values['quest_win'][0], values['quest_win'][1]
    #rotate_and_info: all additional buttons, text and information.
    rotate_and_info = [canvas.create_rectangle(width-30, height-30, width, height, fill='saddle brown', tag='rotate'),
        canvas.create_polygon(width-23, height-23, width-7, height-23, width-14, height-7, fill='black', state=tkinter.DISABLED),
        canvas.create_polygon(width-23, height-23, width-7, height-14, width-23, height-7, fill='white', state=tkinter.HIDDEN),
        canvas.create_rectangle(0, height-30, 30, height, fill='saddle brown', tag='info'),
        canvas.create_text(15, height-15, anchor='center', fill='white', font='Arial 16 bold', text='i', state=tkinter.DISABLED),
        canvas.create_rectangle(0, 0, width, height, fill=values['colors'][1], state=tkinter.HIDDEN, tag='hid'),
        canvas.create_text(0,0, anchor='nw', text=information, state=tkinter.HIDDEN)]
    
    def make_choice(e):
        '''
        При нажатии кнопки на объекте, его данные передаются в эту функцию (Извлекается тег, и по нему принимается решение)
        When you click on an object, its data is transferred to this function (recoverable tag, and it is decided)
        '''
        try:
            event = canvas.gettags(tkinter.CURRENT)[0]
        except:
            #Клик в пустое поле. Click in an empty field.
            return None
        if event == 'rotate':
            if values['buttons_position'] == 'hor':
                values['buttons_position'] = 'vert'
                canvas.itemconfig(rotate_and_info[1], state=tkinter.HIDDEN)
                canvas.itemconfig(rotate_and_info[2], state=tkinter.DISABLED)
            elif values['buttons_position'] == 'vert':
                values['buttons_position'] = 'hor'
                canvas.itemconfig(rotate_and_info[1], state=tkinter.DISABLED)
                canvas.itemconfig(rotate_and_info[2], state=tkinter.HIDDEN)
        elif event == 'info':
            canvas.itemconfig(rotate_and_info[5], state=tkinter.NORMAL, tag='vis')
            canvas.itemconfig(rotate_and_info[6], state=tkinter.DISABLED)
        elif event == 'vis':
            canvas.itemconfig(rotate_and_info[5], state=tkinter.HIDDEN, tag='hid')
            canvas.itemconfig(rotate_and_info[6], state=tkinter.HIDDEN)
        else:
            game_window(win, event)
            canvas.destroy()
    
    canvas.bind('<Button-1>', make_choice)

def game_window(win, size):
    '''
    Окно игры. Здесь создаются все холсты, кнопки и сама игра.
    The game window. Here are all the canvases, buttons, and the game self.
    '''
    #win.overrideredirect(False)
    win.geometry('+10+10')
    
    can_info, can_board, can_buttons = make_canvases(win, size)
    game = Game(can_board, size)
    
    color_buttons = [make_color_buttons(can_buttons, i, size) for i in range(6)]
    
    def color_button_clicked(e):
        '''
        При нажатии кнопки на объекте, его данные передаются в эту функцию (Извлекается тег, и по нему принимается решение)
        When you click on an object, its data is transferred to this function (recoverable tag, and it is decided)
        '''
        try:
            event = can_buttons.gettags(tkinter.CURRENT)[0]
        except:
            return None
        if game.count.state():
            game.make_move(int(event))
        else:
            game.make_end()
    #Привязка собития к холсту. Binding events to this canvas.
    can_buttons.bind('<Button-1>', color_button_clicked)    
    
    def keyboard_clicked(e):
        '''
        При нажатии кнопки на клавиатуре, данные передаются в эту функцию.
        When you click on keyboard, its data is transferred to this function.
        '''
        #Получить значение (имя кнопки) из события. Get the value (button name) of the event.
        event = e.char
        keys = ('1', '2', '3', '4', '5', '6')
        if event in keys:
            if game.count.state():
                game.make_move(int(event)-1)
            else:
                game.make_end()
    
    can_buttons.bind('<Key>', keyboard_clicked)
    #Привязка событий с клавиатуры к этому холсту. Binding events from the keyboard to this canvas.
    can_buttons.focus_set()
    
    info_buttons = make_info_buttons(can_info, size, game.count)
    
    def info_button_clicked(e):
        try:
            event = can_info.gettags(tkinter.CURRENT)[0]
        except:
            return None
        #Ход назад. Undo one move.
        if event == 'undo':
            game.make_undo()
        #Начало новой игры. Start new game.
        elif event == 'new':
            game.destroy()
            can_buttons.destroy()
            can_board.destroy()
            can_info.destroy()
            game_window(win, size)
        else: pass
        
    can_info.bind('<Button-1>', info_button_clicked)
    
    
if __name__ == "__main__":
    window = tkinter.Tk()
    window.title('Color Flood')
    window.resizable(0,0)
    choice_window(window)

    window.mainloop()
