# для работы нужны пакеты: pygame, pygame-popup

import pygame as pg

import random

import datetime
import time

import pygamepopup as pgpu
from pygamepopup.menu_manager import MenuManager

from enum import Enum    


# состояние ячейки
class Cell(Enum):
    EMPTY = 0 # свободна
    WHITE = 1 # занята черными
    BLACK = 2 # занята белыми


class Game:
    # Задаем переменные для цветов 
    white = (255, 255, 255)
    black = (0, 0, 0)
    green = (0, 255, 0)
    alpha_green = (0, 255, 0, 100)

    red = (255, 0, 0)
    alpha_red = (255, 0, 0, 100)
    bone = (226, 216, 201)

    # цвета фишек
    chip_colors = {
        Cell.BLACK : black,
        Cell.WHITE : white
    }

    # шрифты
    wineer_font = None

    # Задаем умолчания переменны для границ игрового поля
    display_width = 800
    display_height = 800
    full_screen = False

    # поверхность, где игра играеться
    display = None
    # время
    clock = None

    # размер поля, умолчание 8 на 8
    n_cells = 8
    # размер одной ячейки на доске
    cell_w = display_width / n_cells
    cell_h = display_height / n_cells

    # интервалы каждого столбца и строки
    cols = []
    rows = []

    # массив с информацией о размешении ячеек столбцах
    cells = None
    # сколько нужно в ряд для победы
    win_condition = 4

    # Кто ходит
    player_turn = None
    # ничья
    draw = False

    # радиус фишки
    chip_radius = 0

    # флаг конца игры
    game_over = False
    # флаг закрытия игры
    game_close = False
    # игра оборвана в процесса
    game_halt = False


    # позиция курсора мышки
    mouse_pos = tuple()

    # немного статистики  
    # когда состоялась игра
    time_started = None
    # сколько ходов было сделано
    n_turns = 0
    # сколько секунд было потрачено на игру
    sec = 0

    # словарь с настройками
    settings = dict()

    # пародия на ИИ
    ai = False

    def __init__(self, display_width = 800, display_height = 800, full_screen = False, ai = False):
        # инициализация
        pg.init()

        # инициализация шрифтов
        pg.font.init()
        self.wineer_font = pg.font.SysFont('Comic Sans MS', 30)

        # ширина и высота дисплея
        self.display_width = display_width
        self.display_height = display_height

        try:
            with open('config.txt', 'r', encoding='utf-8') as fd:
                self.settings = dict([item.split() for item in fd.readlines()])
        except ValueError:
            print("EXCEPTION!!!!")
            pass
        
        print(self.settings)
        # количество ячеек в строке и столбце
        self.n_cells = int(self.settings.get('cells', 8))
        self.win_condition = int(self.settings.get('win_condition', 8))
        self.ai = ai

        self.full_screen = full_screen

        # создаем игровое поле, размеры которого можно изменять
        
        if self.full_screen:
            flags = pg.DOUBLEBUF | pg.FULLSCREEN
            self.display = pg.display.set_mode((0, 0), flags, 32)
            infoObject = pg.display.Info()
            self.display_width = infoObject.current_w
            self.display_height = infoObject.current_h
            print(self.display_width, self.display_height)
        else:
            self.display = pg.display.set_mode((display_width, display_height), pg.DOUBLEBUF, 32)
        # обновляем игровое поле
        pg.display.update() # flip() - похож, но обновляет все, Update - так - целиком

        pg.display.set_caption("4 в ряд")

        self.clock = pg.time.Clock()

        # размер одной ячейки на доске
        self.cell_w = self.display_width / self.n_cells
        self.cell_h = self.display_height / self.n_cells

        # радиус фишки
        self.chip_radius = (self.cell_w / 2) - 10

        # заполняем интервалы для строк и столбцов
        for i in range(self.n_cells):
            self.cols.append((self.cell_w * i, self.cell_w * i + self.cell_w))
            self.rows.append((self.cell_h * i, self.cell_h * i + self.cell_h))

        # создаем массив с информацией о ячейках
        self.cells = [[Cell.EMPTY]*self.n_cells for _ in range(self.n_cells)]

        # первыми ходят белые
        self.player_turn = Cell.WHITE
    
    # получить столбец, над которым сейчас находиться курсор мышки
    def get_col(self, position = None):
        if (position == None):
            x = self.mouse_pos[0]
        else:
            x = position[0]
        for i, item in enumerate(self.cols):    
            # если координата x позиции курсора мыши попадаем в диапазаон столбца,
            # возвращаем номер столбца и его интервал (координаты по x)
            if item[0] <= x and item[1] >= x:
                return i, item
    
    # можно ли ходить в данный столбце
    def is_col_allowed(self, position):
        j, coords = self.get_col(position)
        # нужно проверить, что первая строка i столбца содержит значение EMPTY
        # столбце у нас уже есть, это i, осталось проверить строки
        if self.cells[0][j] == Cell.EMPTY:
            return True
        return False
    
    # подсветить столбце на поле
    def higlight_col(self):
        # получаем номер столбца и его координаты
        j, coords = self.get_col()
        # создаем поверхность, поддерживающую альфа канал
        s = pg.Surface((self.cell_w, self.display_height), pg.SRCALPHA)   # per-pixel alpha
        
        # какой цвет показывать
        # если столбец разрешен, то зеленый
        clr = self.alpha_green
        if not self.is_col_allowed(self.mouse_pos):
            clr = self.alpha_red
        # если нет, то красный

        # рисуем на альфа поверхности прямоугольник
        pg.draw.rect(s, clr, s.get_rect())
        # отображаем на игровом поле новую альфа поверхность
        self.display.blit(s, (coords[0],0))

        # отображать вспомогательную фишку, чтобы было понятно, чей ход
        x_center = coords[0] + ((coords[1] - coords[0]) / 2)
        pg.draw.circle(self.display, self.chip_colors[self.player_turn], (x_center, 0), self.chip_radius)

    # нарисовать игровую доску
    def draw_board(self):
        # нарисовать вертикальные разделители
        for item in self.cols:
            pg.draw.line(self.display, self.black, (item[1], 0), (item[1], self.display_height), 2)
        # нарисовать горизонтальные разделители
        for item in self.rows:
            pg.draw.line(self.display, self.black, (0, item[1]), (self.display_width, item[1]), 2)
        # нарисовать фишки
        for i in range(self.n_cells):
            for j in range(self.n_cells):
                # если ячейка пустая, пропускаем её
                if self.cells[i][j] == Cell.EMPTY:
                    continue
                # иначе, нам нужны границы прямоугольника ячейки
                x1, x2 = self.cols[j]
                y1, y2 = self.rows[i]
                # получаем цент фишки
                x_center, y_center = x1 + ( (x2 - x1) / 2), y1 + ((y2 - y1) / 2)
                pg.draw.circle(self.display, self.chip_colors[self.cells[i][j]], (x_center, y_center), self.chip_radius)

    def render_multi_line(self, text, x, y, fsize):
        lines = text.splitlines()
        for i, l in enumerate(lines):
            self.display.blit(self.wineer_font.render(l, 0, self.black, self.white), (x, y + fsize*i))

    def win_message(self):
        self.game_over = True
        winner = "Белые" if self.player_turn == Cell.WHITE else "Черные"
        winner += ' победили'
        if (self.draw):
            winner = "Ничья"
        msg = f"{winner}.\nИгра длилась {self.sec} секунд.\nХодов сделано: {self.n_turns}\nESC для выхода"
        self.render_multi_line(msg, 0, 0, 40)
        
        #text_surface = self.wineer_font.render(msg, False, (0, 0, 0), self.white)
        #self.display.blit(text_surface, (0,0))

    # проверить условия победы
    def check_win(self, row, col):
        # победа достигаеться, если по диагонале, вертикале и горизонтали 4 в ряд одного цвета
        # проверять есть смылс только на последней вставленной фишке
        # но проверять нужно все целиком, всю диагональ, всю горизонталь и вертикаль
        # в конфиге может быть изменено условие победы
        # выясняем, чей был ход. Для этого цвета выполняется проверка
        player_color = self.cells[row][col]

        cnt = 0
        # проверяем горизонталь
        for j in range(self.n_cells):
            if self.cells[row][j] == player_color:
                cnt += 1
                if cnt >= self.win_condition:
                    return True
            else:
                cnt = 0

        cnt = 0
        # проверяем вертикаль
        for i in range(self.n_cells):
            if self.cells[i][col] == player_color:
                cnt += 1
                if cnt >= self.win_condition:
                    return True
            else:
                cnt = 0

        cnt = 0
        # проверяем главую диагональ
        r = row
        c = col
        # откуда начинать для главной диагонали
        # переходи в саму левую верхнюю клетку диагнонали
        while r >= 0 and c >= 0:
            r -= 1
            c -= 1

        # а затем проходим по всей диагонали
        while r < self.n_cells and c < self.n_cells:
            if self.cells[r][c] == player_color:
                cnt += 1
                if cnt >= self.win_condition:
                    return True
            else:
                cnt = 0
            # переходим на следующую клетку диагонали
            r += 1
            c += 1 

        cnt = 0
        # проверить побочную диагональ
        r = row
        c = col
        # откуда начинать для побочной диагонали
        # переходи в правую верхнюю клетку диагнонали
        while r > 0 and c < self.n_cells-1:
            # строки уменьшются (идем вверх)
            r -= 1
            # столбцы увеличиваються (идем вправо)
            c += 1
        # а затем проходим по всей диагонали

        while r < self.n_cells and c >= 0:
            if self.cells[r][c] == player_color:
                cnt += 1
                if cnt >= self.win_condition:
                    return True
            else:
                cnt = 0
            # мы имед влево вниз, поэтому столбцы влево, а строки вниз
            r += 1
            c -= 1
        
        #если клетки кончились, значит ничья
        if (self.n_turns == self.n_cells * self.n_cells):
            self.draw = True
            return True

    def can_move(self, position):
        return self.is_col_allowed(position)

    # добавить фишку на поле
    def add_chip(self, position):
        
        # фишка была добавлена, увеличиваем количество ходов на 1
        self.n_turns += 1

        # получаем колонку и её координаты
        j, coords = self.get_col(position)
        
        # нужно для проверки условия победы
        row, col = 0, 0
        # находим первую свободную ячейку в столбец и заменяем на цвет ходящего
        # МАССИВ СТРОИТЬСЯ СНИЗУ
        for i in range(self.n_cells-1, -1, -1):
            if self.cells[i][j] == Cell.EMPTY:
                # долбаное равно
                self.cells[i][j] = self.player_turn
                row, col = i, j
                break

        # после вставки фишки, нужно проверить, был ли это победный ход
        # передаем индексы, куда был вставлен элемент
        return self.check_win(row, col)

    # передать ход следующему игроку
    def next_turn(self):
        if self.player_turn == Cell.WHITE:
            self.player_turn = Cell.BLACK
        else:
            self.player_turn = Cell.WHITE
    
    def write_out_results(self):
        winner = 'Белые' if self.player_turn == Cell.WHITE else 'Черные'
        if(self.draw):
            winner = "Ничья"
        field_size = f'{self.n_cells}x{self.n_cells}'
        mode = 'AI' if self.ai else 'PVP'
        res = f"{self.time_started} {self.n_turns} {field_size} {self.win_condition} {self.sec} {mode} {winner}\n"
        
        # если файла нет его нужно создать
        try:
            with open('4_in_row_results.txt', 'r') as fd:
                pass
        except:
            open('4_in_row_results.txt', 'w', encoding='utf-8').close()

        with open('4_in_row_results.txt', 'r+', encoding='utf-8') as fd:
            content = fd.read()
            fd.seek(0, 0)
            fd.write(res + content)

    # очень умный ии
    # простой рандом.
    def ai_move(self):
        # получить разрешенные колонки
        # выбрать случайно одну из них
        while True:
            j = random.randint(0, self.n_cells-1)
            col = self.cols[j]
            coords = (col[0] + 1, col[1]-1)
            if (self.can_move(coords)):
                break
        
        return self.add_chip(coords)
        # взять координаты колонки и передать их функции add_chip

    # начать игру
    def start(self):
        # когда началась игра
        self.time_started = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # начало отсчета тиков
        start_ticks = pg.time.get_ticks()
        while not self.game_over:
            self.draw_board()
            for event in pg.event.get():
                # исли тип события - выхода (кнопка закрытия окна теперь работает)
                if event.type == pg.QUIT:
                    self.game_over = True
                    self.game_halt = True
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.game_over = True
                        self.game_halt = True
                        return
                if event.type == pg.MOUSEMOTION:
                    self.mouse_pos = event.pos
                if event.type == pg.MOUSEBUTTONDOWN:
                    # если в данный столбец можно ходить
                    if self.can_move(event.pos):
                        # если ход не победный, передаем его другому игроку
                        if not (self.add_chip(event.pos)):
                            self.next_turn()
                            # если у нас второй игрок это ИИ
                            if (self.ai):
                                # если ход ИИ не победный
                                if not self.ai_move():
                                    # после хода ИИ ход возвращаеться к нам
                                    self.next_turn()
                                else:
                                    self.game_over=True
                        else:
                            self.game_over = True
            if len(self.mouse_pos):
                self.higlight_col()
            if self.game_over:
                self.draw_board() # последнюю фишку тоже показать надо
                while not self.game_close:
                    self.win_message()
                    for event in pg.event.get():
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_ESCAPE:
                                self.game_close = True
                    pg.display.update()
            pg.display.update()
            self.display.fill(self.bone)
            self.sec = (pg.time.get_ticks()-start_ticks)/1000
            self.clock.tick(60)
        # по завершению игры нужно записать результат в файл результатов
        self.write_out_results()