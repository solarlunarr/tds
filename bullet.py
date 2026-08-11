import pygame as pg
import math

class Bullet(pg.sprite.Sprite):
    def __init__(self, image, x, y, target, damage):
        pg.sprite.Sprite.__init__(self)
        self.original_image = image
        # Use precise floats for x and y position tracking
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.speed = 15  # Bullet speed in pixels per frame

        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.x), int(self.y))

    def update(self):
        # 1. Destroy bullet if target is already dead or removed from game
        if not self.target.alive() or self.target.health <= 0:
            self.kill()
            return

        # 2. Get target coordinates safely (supports Vector2 pos or rect.center)
        if hasattr(self.target, 'pos'):
            target_x, target_y = self.target.pos[0], self.target.pos[1]
        else:
            target_x, target_y = self.target.rect.centerx, self.target.rect.centery

        # 3. Calculate distance to target
        x_dist = target_x - self.x
        y_dist = target_y - self.y
        dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

        # 4. Check if bullet reached or passed target this frame
        if dist <= self.speed:
            # HIT TARGET! Deal damage
            self.target.health -= self.damage
            print(f"Hit! Enemy health remaining: {self.target.health}")
            self.kill()
        else:
            # Rotate bullet toward target
            angle = math.degrees(math.atan2(-y_dist, x_dist))
            self.image = pg.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect()

            # Move using precise float math
            self.x += (x_dist / dist) * self.speed
            self.y += (y_dist / dist) * self.speed
            self.rect.center = (int(self.x), int(self.y))