# -*- coding: utf-8 -*-
import json
import os

import pygame.font
from pygame.font import SysFont
from pygame import init

init()
# ==================================
with open(f"{os.getcwd()}/config.json", 'r') as f:
    json_config = json.load(f)

# Параметры окна
X_MIN, Y_MIN = json_config["WINDOWS_SETTINGS"]["X_MIN"], json_config["WINDOWS_SETTINGS"]["Y_MIN"]
DISPLAY = (X_MIN, Y_MIN)
FLAGS = 1
FPS = json_config["WINDOWS_SETTINGS"]["FPS"]
CUSTOM_MODE = json_config["MODE"]["CUSTOM"]
OFFICIAL_MODE = json_config["MODE"]["OFFICIAL"]
DEBUG_MODE = json_config["MODE"]["DEBUG"]
# Цветовая палитра
RED = (247, 0, 0)
BLACK = (0, 0, 0)
VIOLET = (126, 10, 204)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GOLDEN = (242, 222, 0)
LIGHT_GREEN = (131, 252, 107)
GREEN = (164, 198, 57)
FOREST_GREEN = (87, 189, 68)

# Параметры персонажа
PLAYER_SIZE = tuple(json_config["WINDOWS_SETTINGS"]["PLAYER_SIZE"])
PLAYER_COLOR = GREEN
PLAYER_MAX_SPEED = json_config["WINDOWS_SETTINGS"]["PLAYER_MAX_SPEED"]
PLAYER_JUMPFORCE = json_config["WINDOWS_SETTINGS"]["PLAYER_JUMPFORCE"]
PLAYER_BONUS_JUMPFORCE = json_config["WINDOWS_SETTINGS"]["PLAYER_BONUS_JUMPFORCE"]
GRAVITY = float(json_config["WINDOWS_SETTINGS"]["GRAVITY"])

# Параметры платформ
PLATFORM_COLOR = FOREST_GREEN
PLATFORM_COLOR_LIGHT = LIGHT_GREEN
PLATFORM_SIZE = (200, 50)
PLATFORM_DISTANCE_GAP = (150, 150)
MAX_PLATFORM_NUMBER = 20
CHANCE_BONUS_SPAWN = 10
BONUS_SIZE = (50, 20)
CHANCE_BREAKABLE_PLATFORM = 1

# Параметры текстур
PLATFORMS = json_config["TEXTURE_SETTINGS"]["PLATFORMS"]
PLATFORMS_BREAKABLE = json_config["TEXTURE_SETTINGS"]["PLATFORMS_BREAKABLE"]
TRAMPOLINE = json_config["TEXTURE_SETTINGS"]["TRAMPOLINE"]
PLAYER_LEFT = json_config["TEXTURE_SETTINGS"]["PLAYER_LEFT"]
PLAYER_RIGHT = json_config["TEXTURE_SETTINGS"]["PLAYER_RIGHT"]

# Параметры шрифта
LARGE_FONT = SysFont("", 128)
L_FONT = SysFont("", 64)
SMALL_FONT = SysFont("arial", 24)
INFO_FONT = SysFont("verdana", 26)
INFO_FONT_IS = pygame.font.Font(f"{os.getcwd()}/resources/models/segoe-ui-symbol.ttf", 24)
INFO_FONT_I = pygame.font.Font(f"{os.getcwd()}/resources/models/segoe-ui-symbol.ttf", 22)
INFO_FONT_IL = pygame.font.Font(f"{os.getcwd()}/resources/models/segoe-ui-symbol.ttf", 20)
INFO_FONT_R = SysFont("verdana", 22)
INFO_FONT_F = SysFont("verdana", 20)
RESULT_FONT = SysFont("verdana", 30)
DEBUG_FONT = SysFont("verdana", 16)
UTF_FONT = pygame.font.Font(f"{os.getcwd()}/resources/models/segoe-ui-symbol.ttf", 16)

# Параметры уровней
SYSTEM_LEVELS = dict(json_config["SYSTEM_LEVELS"])
SYSTEM_RATED = {
    "0": {
        "TITLE": "Новичок",
        "COLOR": "#02F2F2"
    },
    "20": {
        "TITLE": "Ученик",
        "COLOR": "#02F20E"
    },
    "90": {
        "TITLE": "Специалист",
        "COLOR": "#0272F2"
    },
    "200": {
        "TITLE": "Эксперт",
        "COLOR": "#0242F2"
    },
    "600": {
        "TITLE": "Кандидат в мастера",
        "COLOR": "#9602F2"
    },
    "950": {
        "TITLE": "Мастер",
        "COLOR": "#F2C202"
    },
    "1400": {
        "TITLE": "Кондидат в гроссмейстеры",
        "COLOR": "#E34800"
    },
    "2000": {
        "TITLE": "Гроссмейстер",
        "COLOR": "#DE1102"
    },
    "2700": {
        "TITLE": "Международный гроссмейстер",
        "COLOR": "#6B0700"
    },
    "3500": {
        "TITLE": "Легендарный гроссмейстер",
        "COLOR": "#E00099"
    },
}
