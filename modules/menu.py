import pygame
import pygamepopup
from pygamepopup.components import Button, InfoBox, TextElement
from pygamepopup.menu_manager import MenuManager

from game import *

import sys
import os

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800


class MainMenuScene:
    # словарь с настройками
    settings = dict()
    menu_width = 800
    menu_height = 800

    game_width = 800
    game_height = 800

    full_screen = False

    screen = None
    
    def __init__(self):
        try:
            with open('config.txt', 'r', encoding='utf-8') as fd:
                self.settings = dict([item.split() for item in fd.readlines()])
        except ValueError:
            pass

        pygame.init()
        pygame.display.set_caption("Игрыыы!")

        self.menu_width = int(self.settings.get('menu_width', 800))
        self.menu_height = int(self.settings.get('menu_height', 800))

        self.game_width = int(self.settings.get('game_width', 800))
        self.game_height = int(self.settings.get('game_height', 800))

        self.full_screen = bool(int(self.settings.get('full_screen', False)))
        if self.full_screen:
            print("TRUE")
        else:
            print("FALSE")

        pygamepopup.init()

        self.screen = pygame.display.set_mode((self.menu_width, self.menu_height))

        self.menu_manager = MenuManager(self.screen)
        self.exit_request = False

        self.create_main_menu_interface()

    def create_main_menu_interface(self):
        main_menu = InfoBox(
            "4 в ряд",
            [
                [
                    Button(
                        title="Игрок против ИИ",
                        callback=lambda: self.start_game(ai = True),
                    )
                ],
                [
                    Button(
                        title="2 игрока",
                        callback=lambda: self.start_game(ai = False),
                    )
                ],
                [
                    Button(
                        title="Результаты",
                        callback=lambda: self.show_results(),
                    )
                ],
                [
                    Button(
                        title="Как играть?",
                        callback=lambda: self.help(),
                    )
                ],
                [Button(title="Выйти", callback=lambda: self.exit())],
            ],
            has_close_button=False,
        )
        self.menu_manager.open_menu(main_menu)

    # читает из файла результаты игр и выводит информацию о 10 последних
    def show_results(self):
        try:
            with open('4_in_row_results.txt', 'r', encoding='utf-8') as fd:
                lines = ['  |  '.join(line.split(' ')) for line in fd.readlines()]
        except Exception:
            return
        
        result = []
        for line in lines:
            result.append([TextElement(line.rstrip())])
        
        
        result = result[:10]
        result.insert(0, [TextElement('-' * 100, margin=(-10,0,-30,0))])
        result.insert(0, [TextElement('  |  '.join("Дата Время Ход Поле Ряд Время Реж Выиграли".split( )), margin=(0,0,0,60))])

        other_menu = InfoBox(
            "Результаты",
            result,
            width=self.menu_width,
        )

        self.menu_manager.open_menu(other_menu)

    def start_game(self, ai = False):
        game = Game(display_width = self.game_width, display_height = self.game_height, 
                    full_screen = self.full_screen, ai = ai)
        game.start()
        self.screen = pygame.display.set_mode((self.menu_width, self.menu_height))
        pygame.display.set_caption("Игрыыы!")

    def help(self):
        help = InfoBox(
            "Как играть?",
            [
                [
                    TextElement(
                        text="Игроки определяются, кто ходит первым. Первыми ходят Белые"
                    )
                ],
                [
                    TextElement(
                        text="Если столбец подсвечен зеленым, значит можно бросить фишку в него"
                    )
                ],
                [
                    TextElement(
                        text="Вишки падают вниз столбца"
                    )
                ],
                [
                    TextElement(
                        text="Для победы нужно расположить более 4 своих фишек по горизонтали, вертикали, или диагонали"
                    )
                ],
                [
                    TextElement(
                        text="Если ходов больше не остаеться, а победителя нет, то результатом является ничья"
                    )
                ],
            ],
            width=500,
        )
        self.menu_manager.open_menu(help)


    def exit(self):
        self.exit_request = True

    def display(self) -> None:
        self.menu_manager.display()

    def motion(self, position: pygame.Vector2) -> None:
        self.menu_manager.motion(position)

    def click(self, button: int, position: pygame.Vector2) -> bool:
        self.menu_manager.click(button, position)
        return self.exit_request


    def launch(self) -> None:
    
        main_menu_scene = self

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    main_menu_scene.motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 or event.button == 3:
                        running = not main_menu_scene.click(event.button, event.pos)
            self.screen.fill((226, 216, 201))
            main_menu_scene.display()
            pygame.display.update()
        pygame.quit()
        sys.exit()


