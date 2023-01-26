from random import randint, randrange
from pygame import Surface
import asyncio

from resources.models.redirect import Redirect
from resources.models.sprite import Sprite
import config

chance = lambda x: randrange(0, 100) < x


class Bonus(Sprite):
    def __init__(self, parent, color=config.GRAY,
                 force=config.PLAYER_BONUS_JUMPFORCE):
        self.parent = parent
        if config.TRAMPOLINE:
            super().__init__(*self.new_pos_update(),
                             config.BONUS_SIZE[0], config.BONUS_SIZE[1], color, config.TRAMPOLINE)
        else:
            super().__init__(*self.new_pos_update(),
                             config.BONUS_SIZE[0], config.BONUS_SIZE[1], color)
        self.force = force

    def new_pos_update(self):
        x = self.parent.rect.centerx - config.BONUS_SIZE[0] // 2
        y = self.parent.rect.y - config.BONUS_SIZE[1] + 5
        return x, y


class Platform(Sprite):
    def __init__(self, x, y, width, height,
                 initial_bonus=False, breakable=False):

        color = config.PLATFORM_COLOR
        png = config.PLATFORMS
        if breakable:
            color = config.PLATFORM_COLOR_LIGHT
            png = config.PLATFORMS_BREAKABLE
        if png:
            super().__init__(x, y, width, height, color, png)
        else:
            super().__init__(x, y, width, height, color)

        self.breakable = breakable
        self.__level = Level.instance
        self.__bonus = None
        if initial_bonus:
            self.bonus_adding(Bonus)

    @property
    def bonus(self):
        return self.__bonus

    def bonus_adding(self, bonus_type):
        assert issubclass(bonus_type, Bonus), "Type Bonus Error !"
        if not self.__bonus and not self.breakable:
            self.__bonus = bonus_type(self)

    def bonus_removing(self):
        self.__bonus = None

    def the_Collide(self):
        if self.breakable:
            self.__level.platform_removing(self)

    def drawing_sprite(self, surface):
        super().drawing_sprite(surface)
        if self.__bonus:
            self.__bonus.drawing_sprite(surface)
        if self.camera_rect.y + self.rect.height > config.Y_MIN:
            self.__level.platform_removing(self)


class Level(Redirect):
    def __init__(self):
        self.platform_size = config.PLATFORM_SIZE
        self.max_platforms = config.MAX_PLATFORM_NUMBER
        self.distance_min = min(config.PLATFORM_DISTANCE_GAP)
        self.distance_max = max(config.PLATFORM_DISTANCE_GAP)

        self.bonus_platform_chance = config.CHANCE_BONUS_SPAWN
        self.breakable_platform_chance = config.CHANCE_BREAKABLE_PLATFORM

        self.__platforms = []
        self.__to_remove = []

        self.__base_platform = Platform(
            config.X_MIN // 2 - self.platform_size[0] // 2,
            config.Y_MIN // 2 + config.Y_MIN / 3,
            *self.platform_size)

    @property
    def platforms(self):
        return self.__platforms

    async def generating(self):
        nb_to_generate = self.max_platforms - len(self.__platforms)
        for _ in range(nb_to_generate):
            self.platform_generating()

    def platform_generating(self):
        if self.__platforms:
            offset = randint(self.distance_min, self.distance_max)
            self.__platforms.append(Platform(
                randint(0, config.X_MIN - self.platform_size[0]),
                self.__platforms[-1].rect.y - offset,
                *self.platform_size,
                initial_bonus=chance(self.bonus_platform_chance),
                breakable=chance(self.breakable_platform_chance)))
        else:
            self.__platforms.append(self.__base_platform)

    def platform_removing(self, plt):
        if plt in self.__platforms:
            self.__to_remove.append(plt)
            return True
        return False

    def global_position(self):
        self.__platforms = [self.__base_platform]

    def updating(self):
        for platform in self.__to_remove:
            if platform in self.__platforms:
                self.__platforms.remove(platform)
        self.__to_remove = []
        asyncio.run(self.generating())

    def drawing_sprite(self, surface):
        for platform in self.__platforms:
            platform.drawing_sprite(surface)
