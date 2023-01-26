from math import copysign
from pygame.math import Vector2
from pygame.locals import KEYDOWN, KEYUP, K_LEFT, K_RIGHT
from pygame.sprite import collide_rect
from pygame.event import Event

from resources.models.redirect import Redirect
from resources.models.sprite import Sprite
from resources.models.level import Level
import config

getsign = lambda x: copysign(1, x)


class Player(Sprite, Redirect):
    def __init__(self, *args):
        Sprite.__init__(self, *args)
        self.__startrect = self.rect.copy()
        self.__maxvelocity = Vector2(config.PLAYER_MAX_SPEED, 100)
        self.__startspeed = 1.5

        self._velocity = Vector2()
        self._input = 0
        self._jumpforce = config.PLAYER_JUMPFORCE
        self._bonus_jumpforce = config.PLAYER_BONUS_JUMPFORCE

        self.gravity = config.GRAVITY
        self.accel = .5
        self.deccel = .6
        self.dead = False

    def velocity_fixing(self):
        self._velocity.y = min(self._velocity.y, self.__maxvelocity.y)
        self._velocity.y = round(max(self._velocity.y, -self.__maxvelocity.y), 2)
        self._velocity.x = min(self._velocity.x, self.__maxvelocity.x)
        self._velocity.x = round(max(self._velocity.x, -self.__maxvelocity.x), 2)

    def global_position(self):
        self._velocity = Vector2()
        self.rect = self.__startrect.copy()
        self.camera_rect = self.__startrect.copy()
        self.dead = False

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                self._velocity.x = -self.__startspeed
                Sprite.__init__(self,
                                *[self.rect.x,
                                self.rect.y,
                                *config.PLAYER_SIZE,
                                config.PLAYER_COLOR,
                                config.PLAYER_LEFT]
                                )
                self._input = -1
            elif event.key == K_RIGHT:
                self._velocity.x = self.__startspeed
                Sprite.__init__(self,
                                *[self.rect.x,
                                self.rect.y,
                                *config.PLAYER_SIZE,
                                config.PLAYER_COLOR,
                                config.PLAYER_RIGHT]
                                )
                self._input = 1
        elif event.type == KEYUP:
            if (event.key == K_LEFT and self._input == -1) or (
                    event.key == K_RIGHT and self._input == 1):
                self._input = 0

    def jump_event(self, force=None):
        if not force:
            force = self._jumpforce
        self._velocity.y = -force

    def the_Collide(self, obj):
        self.rect.bottom = obj.rect.top
        self.jump_event()

    def Player_boarders(self):
        lvl = Level.instance
        if not lvl:
            return
        for platform in lvl.platforms:
            if self._velocity.y > .5:
                if platform.bonus and collide_rect(self, platform.bonus):
                    self.the_Collide(platform.bonus)
                    self.jump_event(platform.bonus.force)
                if collide_rect(self, platform):
                    self.the_Collide(platform)
                    platform.the_Collide()

    def update(self):
        if self.camera_rect.y > config.Y_MIN * 2:
            self.dead = True
            return
        self._velocity.y += self.gravity
        if self._input:
            self._velocity.x += self._input * self.accel
        elif self._velocity.x:
            self._velocity.x -= getsign(self._velocity.x) * self.deccel
            self._velocity.x = round(self._velocity.x)
        self.velocity_fixing()

        self.rect.x = (self.rect.x + self._velocity.x) % (config.X_MIN - self.rect.width)
        self.rect.y += self._velocity.y

        self.Player_boarders()
