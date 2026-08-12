import pygame as pg
import math
import Constants as c

class Bullet(pg.sprite.Sprite):
    def __init__(self, image, x, y, target_pos, damage):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.damage = damage
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = pg.math.Vector2(x, y)
        self.speed = 10

        # Calculate the direction vector towards the target
        self.direction = (target_pos - self.pos).normalize()
        
        # Calculate angle to rotate the bullet image so it points at the enemy
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.image = pg.transform.rotate(self.image, angle)

    def update(self):
        # Move the bullet
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        # Delete the bullet if it goes off screen to save memory
        if (self.rect.right < 0 or self.rect.left > c.WIDTH + c.SIDE_PANEL or 
            self.rect.bottom < 0 or self.rect.top > c.HEIGHT):
            self.kill()