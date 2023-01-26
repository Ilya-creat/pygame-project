import os
import sys

import pygame
from pygame import Surface, Rect
from resources.models.camera import Camera


class Sprite:
    def __init__(self, x, y, w, h, color, texture=""):
        self.__color = color
        self.texture = texture
        if self.texture:
            self._image = pygame.transform.scale(self.load_image(self.texture), (w, h))
            self.rect = Rect(x, y, w, h)
        else:
            self._image = Surface((w, h))
            self._image.fill(self.color)
            self._image = self._image.convert()
            self.rect = Rect(x, y, w, h)
        self.camera_rect = self.rect.copy()

    @property
    def image(self):
        return self._image

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, new):
        assert isinstance(new, tuple) and len(new) == 3, "Color Error"
        self.__color = new
        self._image.fill(self.color)

    def drawing_sprite(self, surface):
        if Camera.instance:
            self.camera_rect = Camera.instance.moving_apply_rect(self)
            surface.blit(self._image, self.camera_rect)
        else:
            surface.blit(self._image, self.rect)

    def load_image(self, name, colorkey=None):
        fullname = os.path.join(f"{os.getcwd()}/resources/texture/", name)
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
