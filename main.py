
import json
import os
import sqlite3
import sys

import pygame
import pygame_widgets
import cv2
from pygame_widgets.button import Button
import threading
import config
from resources.models.game import Game
from resources.models.sql import SQL

pygame.init()
size = width, height = config.DISPLAY
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Испытай себя')
clock = pygame.time.Clock()
loading_status_widget = False
pygame.mixer.music.load(f"{os.getcwd()}/resources/sounds/main.mp3")
pygame.mixer.music.play(-1)


def terminate():
    exit()


def next_(arg1='start'):
    global widgets
    widgets = arg1


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


def load_image(name, colorkey=None):
    fullname = os.path.join(f"{os.getcwd()}/resources/images", name)
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


loading_gif = loadGIF(rf"{os.getcwd()}/resources/images/loading.gif")
widgets = 'start'

sql = SQL(sqlite3.connect(f"{os.getcwd()}/game.db"))


def loading():
    global loading_gif
    currentFrame = 0
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
        screen.fill((0, 0, 0))
        if loading_status_widget:
            break

        rect = loading_gif[currentFrame].get_rect()
        screen.blit(loading_gif[currentFrame], rect)
        currentFrame = (currentFrame + 1) % len(loading_gif)
        pygame.display.flip()
        clock.tick(20)


def game_info():
    global loading_status_widget
    all_sprites = pygame.sprite.Group()
    gifFrameList = loadGIF(rf"{os.getcwd()}/resources/images/game.gif")
    image_info = pygame.sprite.Sprite(all_sprites)
    image_info.image = load_image("game_info.png")
    image_info.rect = image_info.image.get_rect()
    image_info.rect.y += 40
    all_sprites.add(image_info)
    currentFrame = 0
    back_button = Button(
        screen,
        width - 200,
        90,
        150,
        70,
        text="Назад",
        textColour=(255, 255, 255),
        fontSize=30,
        margin=20,
        inactiveColour=(16, 6, 102),
        hoverColour=(150, 0, 0),
        pressedColour=(0, 200, 20),
        radius=20,
        onClick=lambda: next_('start')
    )
    table = [width, height]
    image = pygame.Surface(table)
    image.fill((0, 0, 0))
    image = image.convert()
    image.set_colorkey((255, 0, 255))
    image.set_alpha(100)
    screen.blit(image,
                (0, 0))
    loading_status_widget = True
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
        if widgets != 'game_info':
            loading_status_widget = False
            threading.Thread(target=loading).start()
            back_button.hide()
            break
        screen.fill((0, 0, 0))
        rect = gifFrameList[currentFrame].get_rect()
        screen.blit(gifFrameList[currentFrame], rect)
        currentFrame = (currentFrame + 1) % len(gifFrameList)

        screen.blit(image,
                    (config.X_MIN // 2 - table[0] // 2, config.Y_MIN // 2 - table[1] // 2))
        all_sprites.update(screen)
        all_sprites.draw(screen)
        pygame_widgets.update(events)
        pygame.display.update()
        clock.tick(20)


def statistics_game():
    global loading_status_widget
    all_sprites = pygame.sprite.Group()
    gifFrameList = loadGIF(rf"{os.getcwd()}/resources/images/main.gif")
    currentFrame = 0
    back_button = Button(
        screen,
        1025,
        600,
        150,
        70,
        text="Назад",
        textColour=(255, 255, 255),
        fontSize=30,
        margin=20,
        inactiveColour=(16, 6, 102),
        hoverColour=(150, 0, 0),
        pressedColour=(0, 200, 20),
        radius=20,
        onClick=lambda: next_('start')
    )
    s = sql.get_session()
    get_max = ["0", "0", "0", "0", "0"]
    rating = 0
    for i in s:
        if int(get_max[1]) <= i[1] and i[5] != "custom":
            get_max[0] = str(i[0])
            get_max[1] = str(i[1])
            get_max[3] = str(i[2]) + " сек."
            get_max[2] = str(i[3])
            get_max[4] = str(i[4])
        rating += i[4]
    title = ["", ""]
    for k, v in config.SYSTEM_RATED.items():
        if int(k) <= rating:
            title[0] = v["TITLE"]
            title[1] = v["COLOR"]
    if title[1] == "":
        title[0] = "нет звания :("
        title[1] = "#EBAEAE"
    rating = round(rating, 3)
    text = "Статистика игры"
    text1 = "Общие сведения:"
    text2 = "◆ Rating:"
    text3 = "◆ Title:"
    text4 = "Лучший результат:"
    text_session = "Сессия: "
    text_score = "Пройдено метров: "
    text_time = "Время игры: "
    text_levels = "Достигнутый уровень: "
    text_rating = "Полученный рейтинг: "
    text_session_1 = "Сессия "
    text_score_1 = "Пройдено (м)"
    text_time_1 = "Время (сек)"
    text_levels_1 = "Уровень "
    text_rating_1 = "Рейтинг "
    text_ops = "▲"
    text_ops_1 = "▲"
    text_ops_2 = "▼"
    text_op = "▶"
    text5 = "Последние сессии: "
    text_op = config.INFO_FONT_I.render(text_op, 1, title[1])
    title[0] = config.INFO_FONT_R.render(title[0], 1, title[1])
    rating = config.INFO_FONT_R.render(str(rating), 1, title[1])
    text = config.L_FONT.render(text, 1, config.GOLDEN)
    text1 = config.INFO_FONT.render(text1, 1, config.RED)
    text2 = config.INFO_FONT_I.render(text2, 1, config.WHITE)
    text3 = config.INFO_FONT_I.render(text3, 1, config.WHITE)
    text4 = config.INFO_FONT.render(text4, 1, config.RED)
    text5 = config.INFO_FONT.render(text5, 1, config.RED)
    text_ops = config.INFO_FONT_I.render(text_ops, 1, config.GREEN)
    text_ops_1 = config.INFO_FONT_IL.render(text_ops_1, 1, config.GREEN)
    text_ops_2 = config.INFO_FONT_IL.render(text_ops_2, 1, config.RED)
    get_max[0] = config.INFO_FONT_R.render(get_max[0], 1, config.WHITE)
    get_max[1] = config.INFO_FONT_R.render(get_max[1], 1, config.WHITE)
    get_max[2] = config.INFO_FONT_R.render(get_max[2], 1, config.WHITE)
    get_max[3] = config.INFO_FONT_R.render(get_max[3], 1, config.WHITE)
    get_max[4] = config.INFO_FONT_R.render(get_max[4], 1, config.WHITE)
    text_session = config.INFO_FONT_R.render(text_session, 1, config.GOLDEN)
    text_score = config.INFO_FONT_R.render(text_score, 1, config.GOLDEN)
    text_time = config.INFO_FONT_R.render(text_time, 1, config.GOLDEN)
    text_levels = config.INFO_FONT_R.render(text_levels, 1, config.GOLDEN)
    text_rating = config.INFO_FONT_R.render(text_rating, 1, config.GOLDEN)
    text_session_1 = config.INFO_FONT_F.render(text_session_1, 1, config.GOLDEN)
    text_score_1 = config.INFO_FONT_F.render(text_score_1, 1, config.GOLDEN)
    text_time_1 = config.INFO_FONT_F.render(text_time_1, 1, config.GOLDEN)
    text_levels_1 = config.INFO_FONT_F.render(text_levels_1, 1, config.GOLDEN)
    text_rating_1 = config.INFO_FONT_F.render(text_rating_1, 1, config.GOLDEN)
    ans = []
    ind = 9
    for i in s:
        if i[5] != "custom":
            k = [0, 0, 0, 0, [0, 0]]
            k[0] = config.INFO_FONT_F.render(str(i[0]), 1, config.WHITE)
            k[1] = config.INFO_FONT_F.render(str(i[1]), 1, config.WHITE)
            k[3] = config.INFO_FONT_F.render(str(i[2]), 1, config.WHITE)
            k[2] = config.INFO_FONT_F.render(str(i[3]), 1, config.WHITE)
            k[4][0] = config.INFO_FONT_F.render(str(i[4]) if i[4] >= 0 else str(i[4])[1:], 1, config.WHITE)
            k[4][1] = i[4]
            ans.append(k)
            ind -= 1
        if ind == 0:
            break
    table = [1100, 650]
    image = pygame.Surface(table)
    image.fill((0, 0, 0))
    image = image.convert()
    image.set_colorkey((255, 0, 255))
    image.set_alpha(100)
    loading_status_widget = True
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
        if widgets != 'statistics':
            loading_status_widget = False
            threading.Thread(target=loading).start()
            back_button.hide()
            break
        screen.fill((0, 0, 0))
        rect = gifFrameList[currentFrame].get_rect()
        screen.blit(gifFrameList[currentFrame], rect)
        currentFrame = (currentFrame + 1) % len(gifFrameList)
        screen.blit(image,
                    (config.X_MIN // 2 - table[0] // 2, config.Y_MIN // 2 - table[1] // 2))
        screen.blit(text, (config.X_MIN // 2 - text.get_width() // 2, 60))
        screen.blit(text1, (150, 100))
        screen.blit(text2, (170, 140))
        screen.blit(rating, (275, 140))
        screen.blit(text3, (170, 170))
        screen.blit(text_op, (275, 170))
        screen.blit(title[0], (300, 170))
        screen.blit(text4, (150, 200))
        screen.blit(get_max[0], (450, 230))
        screen.blit(get_max[1], (450, 260))
        screen.blit(get_max[2], (450, 290))
        screen.blit(get_max[3], (450, 320))
        screen.blit(get_max[4], (470, 350))
        screen.blit(text_ops, (450, 350))
        screen.blit(text_session, (170, 230))
        screen.blit(text_score, (170, 260))
        screen.blit(text_time, (170, 290))
        screen.blit(text_levels, (170, 320))
        screen.blit(text_rating, (170, 350))
        screen.blit(text5, (150, 380))
        screen.blit(text_session_1, (170, 410))
        screen.blit(text_score_1, (270, 410))
        screen.blit(text_levels_1, (450, 410))
        screen.blit(text_time_1, (550, 410))
        screen.blit(text_rating_1, (700, 410))
        sk = 440
        for i in ans:
            screen.blit(i[0], (190, sk))
            screen.blit(i[1], (290, sk))
            screen.blit(i[2], (480, sk))
            screen.blit(i[3], (580, sk))
            if i[4][1] < 0:
                screen.blit(text_ops_2, (710, sk))
                screen.blit(i[4][0], (730, sk))
            else:
                screen.blit(text_ops_1, (710, sk))
                screen.blit(i[4][0], (730, sk))
            sk += 25
        all_sprites.update(screen)
        all_sprites.draw(screen)
        pygame_widgets.update(events)
        pygame.display.update()
        clock.tick(20)


def start_game():
    global loading_status_widget
    game = Game(sql)
    loading_status_widget = True
    status = game.starting_thegame_moving()
    if status == "exit":
        terminate()
    if status == "break":
        loading_status_widget = False
        threading.Thread(target=loading).start()
        next_("start")
    if status == "ok":
        next_("")
    if status == "restart":
        loading_status_widget = False
        start_game()


def start_screen():
    global loading_status_widget
    all_sprites = pygame.sprite.Group()
    gifFrameList = loadGIF(rf"{os.getcwd()}/resources/images/main.gif")
    image_info = pygame.sprite.Sprite(all_sprites)
    image_info.image = load_image("gamelogo.png")
    image_info.rect = image_info.image.get_rect()
    all_sprites.add(image_info)
    currentFrame = 0
    start_game_button = Button(
        screen,
        width // 2 - 150,
        height // 2 - 50,
        300,
        100,
        text="Играть",
        textColour=(255, 255, 255),
        fontSize=30,
        margin=20,
        inactiveColour=(16, 6, 102),
        hoverColour=(150, 0, 0),
        pressedColour=(0, 200, 20),
        radius=20,
        onClick=lambda: next_('play')
    )
    statistics_button = Button(
        screen,
        width // 2 - 150,
        height // 2 - 50 + start_game_button.getHeight() + 20,  # Y
        300,
        100,
        text="Статистика",
        textColour=(255, 255, 255),
        fontSize=30,
        margin=20,
        inactiveColour=(16, 6, 102),
        hoverColour=(150, 0, 0),
        pressedColour=(0, 200, 20),
        radius=20,
        onClick=lambda: next_('statistics')
    )
    game_info_button = Button(
        screen,
        width // 2 - 150,
        height // 2 - 50 + (start_game_button.getHeight() + 20) * 2,  # Y
        300,
        100,
        text="Правила",
        textColour=(255, 255, 255),
        fontSize=30,
        margin=20,
        inactiveColour=(16, 6, 102),
        hoverColour=(150, 0, 0),
        pressedColour=(0, 200, 20),
        radius=20,
        onClick=lambda: next_('game_info')
    )
    loading_status_widget = True
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
        if widgets != 'start':
            loading_status_widget = False
            threading.Thread(target=loading).start()
            start_game_button.hide()
            statistics_button.hide()
            start_game_button.hide()
            game_info_button.hide()
            break
        screen.fill((0, 0, 0))

        rect = gifFrameList[currentFrame].get_rect()
        screen.blit(gifFrameList[currentFrame], rect)
        currentFrame = (currentFrame + 1) % len(gifFrameList)

        all_sprites.update(screen)
        all_sprites.draw(screen)
        pygame_widgets.update(events)
        pygame.display.update()
        clock.tick(20)


def main():
    global widgets
    threading.Thread(target=loading).start()
    try:
        with open("config.json", 'r') as f:
            json_ = json.load(f)
            if not json_ or json_["MODE"]["OFFICIAL"] and not json_["MODE"]["DEBUG"]:
                s = open(f"{os.getcwd()}/resources/models/official.json", 'r')
                json_ = json.load(s)
                with open("config.json", 'w') as fw:
                    json.dump(json_, fw, ensure_ascii=False, indent=4)
            if json_["MODE"]["OFFICIAL"] and json_["MODE"]["DEBUG"]:
                s = open(f"{os.getcwd()}/resources/models/official.json", 'r')
                json_ = json.load(s)
                json_["MODE"]["DEBUG"] = True
                with open("config.json", 'w') as fw:
                    json.dump(json_, fw, ensure_ascii=False, indent=4)
    except Exception as e:
        s = open(f"{os.getcwd()}/resources/models/official.json", 'r')
        json_ = json.load(s)
        with open("config.json", 'w') as fw:
            json.dump(json_, fw, ensure_ascii=False, indent=4)
    while True:
        if widgets == 'start':
            start_screen()
        if widgets == 'statistics':
            statistics_game()
        if widgets == "play":
            start_game()
        if widgets == "game_info":
            game_info()


if __name__ == "__main__":
    main()
