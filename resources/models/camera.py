from pygame import Rect

import config
from resources.models.redirect import Redirect


class Camera(Redirect):

    def __init__(self, lerp=3, width=config.X_MIN, height=config.Y_MIN):
        self.state = Rect(0, 0, width, height)
        self.lerp = lerp
        self.center = height // 2
        self.maxheight = self.center

    def global_position(self):
        self.state.y = 0
        self.maxheight = self.center

    def rect_moving(self, rect):
        return rect.move((0, -self.state.topleft[1]))

    def moving_apply_rect(self, target):
        return self.rect_moving(target.rect)

    def updating(self, target):
        if target.y < self.maxheight:
            self.lastheight = self.maxheight
            self.maxheight = target.y
        speed = ((self.state.y + self.center) - self.maxheight) / self.lerp
        self.state.y -= speed
