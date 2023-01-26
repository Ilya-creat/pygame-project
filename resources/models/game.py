import os
import sys
import time

import pygame
import pygame_widgets

from resources.models.camera import Camera
from resources.models.player import Player
from resources.models.level import Level
from pygame_widgets.button import Button
import config
import cv2
from pygame.math import Vector2


def cv2ImageToSurface(cv2Image):
    size = cv2Image.shape[1::-1]
    format = 'RGBA' if cv2Image.shape[2] == 4 else 'RGB'
    cv2Image[:, :, [0, 2]] = cv2Image[:, :, [2, 0]]
    surface = pygame.image.frombuffer(cv2Image.flatten(), size, format)
    return surface.convert_alpha() if format == 'RGBA' else surface.convert()


def loadGIF(filename):
    gif = cv2.VideoCapture(filename)
    frames = []
    while True:
        ret, cv2Image = gif.read()
        if not ret:
            break
        pygameImage = cv2ImageToSurface(cv2Image)
        frames.append(pygameImage)
    return frames


class Game:
    def __init__(self, sql):
        self._alive = True
        self.window = pygame.display.set_mode(config.DISPLAY, config.FLAGS)
        self.clock = pygame.time.Clock()
        self.status = "ok"
        self.currentFrame = 0
        self.gifFrameList = loadGIF(rf"{os.getcwd()}/resources/images/game.gif")

        self.camera = Camera()
        self.lvl = Level()
        self.player = Player(
            config.X_MIN / 2 - config.PLAYER_SIZE[0] / 2,
            config.Y_MIN / 2 + config.Y_MIN / 2 / 2,
            *config.PLAYER_SIZE,
            config.PLAYER_COLOR,
            config.PLAYER_LEFT if config.PLAYER_LEFT else ""
        )

        self.db = sql
        self.levels = 1
        self.score = 0
        self.rating = 0
        self.score_txt = config.SMALL_FONT.render("0 m", 1, config.VIOLET)
        self.score_pos = pygame.math.Vector2(10, 10)
        self.start_time = time.time()
        self.end_time = time.time()
        self.db_r = True
        if config.DEBUG_MODE:
            self.debug_fps = config.DEBUG_FONT.render(f"{self.clock.get_fps():2.0f} FPS", 1, config.WHITE)
            self.debug_fps_pos = pygame.math.Vector2(10, 50)
            self.debug_time = config.DEBUG_FONT.render(f"{(self.end_time - self.start_time)} сек.", 1, config.WHITE)
            self.debug_time_pos = pygame.math.Vector2(10, 70)
            self.debug_levels = config.DEBUG_FONT.render(f"{self.levels} lvl", 1, config.WHITE)
            self.debug_levels_pos = pygame.math.Vector2(10, 90)
            self.debug_rating = config.UTF_FONT.render(f"▲▼{self.rating} rt", 1, config.WHITE)
            self.debug_rating_pos = pygame.math.Vector2(10, 110)
        self.lvl_player = 1
        self.gameover_txt = config.LARGE_FONT.render("Game Over", 1, config.RED)

        self.gameover_rect = self.gameover_txt.get_rect(
            center=(config.X_MIN // 2, config.Y_MIN // 2 - config.Y_MIN // 2 // 2))

        self.restart_game_button = None
        self.return_button = None
        self.table = [1000, 500]
        self.image = pygame.Surface(self.table)
        self.image.fill((0, 0, 0))
        self.image = self.image.convert()
        self.image.set_colorkey((255, 0, 255))
        self.image.set_alpha(100)
        self.restart_game_button = Button(
            self.window,
            self.image.get_rect().x + self.image.get_height() - 170,
            self.table[1],
            150,
            70,
            text="Заново",
            textColour=(255, 255, 255),
            fontSize=30,
            margin=20,
            inactiveColour=(16, 6, 102),
            hoverColour=(150, 0, 0),
            pressedColour=(0, 200, 20),
            radius=20,
            onClick=lambda: self.event_close("restart")
        )
        self.return_button = Button(
            self.window,
            self.image.get_rect().x + self.image.get_height() - 170 + self.restart_game_button.getWidth() + 10,
            self.table[1],
            150,
            70,
            text="Выйти",
            textColour=(255, 255, 255),
            fontSize=30,
            margin=20,
            inactiveColour=(16, 6, 102),
            hoverColour=(150, 0, 0),
            pressedColour=(0, 200, 20),
            radius=20,
            onClick=lambda: self.event_close("break")
        )

    def event_close(self, e):
        self._alive = False
        self.status = e

    def global_position(self):
        self.camera.global_position()
        self.lvl.global_position()
        self.player.global_position()

    def loop_start(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.event_close("exit")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.event_close("break")
                if event.key == pygame.K_RETURN and self.player.dead:
                    self.global_position()
            self.player.handle_event(event)

    def loop_updating(self):
        self.player.update()
        self.lvl.updating()
        if not self.player.dead:
            self.camera.updating(self.player.rect)
            self.score = -self.camera.state.y // 50
            self.score_txt = config.SMALL_FONT.render(
                str(self.score) + " м.", 1, config.VIOLET)
            self.end_time = time.time() - self.start_time
            s = self.db.get_session()
            res = 0
            count_bad = 0
            for i in s:
                res += i[1]
            res += self.score
            res /= len(s) + 1
            if self.score < res:
                self.rating = round(-1000 * ((res - self.score) / 10000), 3)
            else:
                self.rating = round(1000 * ((self.score - res) / 10000), 3)
            if config.DEBUG_MODE:
                self.debug_fps = config.DEBUG_FONT.render(f"{self.clock.get_fps():2.0f} FPS", 1, config.WHITE)
                self.debug_time = config.DEBUG_FONT.render(f"{round(self.end_time)} сек.", 1,
                                                           config.WHITE)
                self.debug_levels = config.DEBUG_FONT.render(f"{self.levels} lvl", 1,
                                                             config.WHITE)
                if config.CUSTOM_MODE:
                    self.debug_rating = config.UTF_FONT.render(f"▲▼ UnRated", 1, config.WHITE)
                else:
                    self.debug_rating = config.UTF_FONT.render(f"▲▼ {self.rating} rt", 1, config.WHITE)
        for k, v in config.SYSTEM_LEVELS.items():
            if self.score - v["SCORE"] >= 0:
                self.levels = int(k)
                Level.instance.bonus_platform_chance = v["CHANCE_BONUS_SPAWN"]
                Level.instance.breakable_platform_chance = v["CHANCE_BREAKABLE_PLATFORM"]

    def loop_rendering(self):
        rect = self.gifFrameList[self.currentFrame].get_rect()
        self.window.blit(self.gifFrameList[self.currentFrame], rect)
        self.currentFrame = (self.currentFrame + 1) % len(self.gifFrameList)
        self.lvl.drawing_sprite(self.window)
        self.player.drawing_sprite(self.window)
        if self.player.dead:
            if self.db_r:
                self.db.add_session(self.score, self.levels, round(self.end_time), self.rating, "official" \
                    if config.OFFICIAL_MODE else "custom")
                self.db_r = False
            info_text = "Результаты данной сессии:"
            times_ = {'h': round(self.end_time) // 3600,
                      'm': (round(self.end_time) - 3600 * (round(self.end_time) // 3600)) // 60,
                      's':
                          round(self.end_time) - 60 * (
                                  (round(self.end_time) - 3600 * (round(self.end_time) // 3600)) // 60)}
            words = {'h': ['часов', 'час', 'часа'], 'm': ['минут', 'минута', 'минуты'],
                     's': ['секунд', 'секунда', 'секунды']}
            out = []
            for k, v in times_.items():
                rem = v % 10
                if v == 0 or rem == 0 or rem >= 5 or v in range(11, 19):
                    st = str(v), words[k][0]
                elif rem == 1:
                    st = str(v), words[k][1]
                else:
                    st = str(v), words[k][2]
                out.append(" ".join(st))
            result_text = [
                f"Пройдено: {self.score} м.",
                f"Достигнутый уровень: {self.levels}",
                f"Время прохождения: {' '.join(out)}",
            ]
            self.window.blit(self.image,
                             (config.X_MIN // 2 - self.table[0] // 2, config.Y_MIN // 2 - self.table[1] // 2))
            text_coord = self.image.get_rect()
            text_coord.x += config.X_MIN // 2 - self.table[0] // 2 + 120
            text_coord.y += config.Y_MIN // 2 - self.table[1] // 2 + 120
            self.window.blit(self.gameover_txt, self.gameover_rect)
            string_rendered = config.RESULT_FONT.render(info_text, 1, config.GOLDEN)
            intro_rect = string_rendered.get_rect()
            intro_rect.x = text_coord.x
            intro_rect.y = text_coord.y
            self.window.blit(string_rendered, intro_rect)
            text_coord.y += string_rendered.get_height() + 20
            for i in result_text:
                string_rendered = config.INFO_FONT.render(i, 1, config.WHITE)
                intro_rect = string_rendered.get_rect()
                intro_rect.x = text_coord.x
                intro_rect.y = text_coord.y
                self.window.blit(string_rendered, intro_rect)
                text_coord.y += string_rendered.get_height() + 10
            string_s = "Изменение в рейтинге: "
            string_v = f"{self.rating}"
            string_s = config.INFO_FONT.render(string_s, 1, config.WHITE)
            self.window.blit(string_s, text_coord)
            if self.rating < 0:
                txt = "▼"
                txt = config.INFO_FONT_IS.render(txt, 1, config.RED)
                text_coord.x += 320
                self.window.blit(txt, text_coord)
                text_coord.x += 25
                string_v = config.INFO_FONT.render(string_v[1:], 1, config.WHITE)
                self.window.blit(string_v, text_coord)
            else:
                txt = "▲"
                txt = config.INFO_FONT_IS.render(txt, 1, config.GREEN)
                text_coord.x += 320
                self.window.blit(txt, text_coord)
                text_coord.x += 25
                string_v = config.INFO_FONT.render(string_v, 1, config.WHITE)
                self.window.blit(string_v, text_coord)
            events = pygame.event.get()
            pygame_widgets.update(events)
        self.window.blit(self.score_txt, self.score_pos)
        if config.DEBUG_MODE:
            self.window.blit(self.debug_fps, self.debug_fps_pos)
            self.window.blit(self.debug_time, self.debug_time_pos)
            self.window.blit(self.debug_levels, self.debug_levels_pos)
            self.window.blit(self.debug_rating, self.debug_rating_pos)
        pygame.display.update()
        self.clock.tick(config.FPS)

    def starting_thegame_moving(self):
        while self._alive:
            if not self.player.dead:
                self.db_r = True
                self.loop_start()
                self.loop_updating()
                self.loop_rendering()
            else:
                self.loop_start()
                self.loop_rendering()
        self.restart_game_button.hide()
        self.return_button.hide()
        return self.status

    def load_image(self, name, colorkey=None):
        fullname = os.path.join(f"{os.getcwd()}/resources/texture", name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image
