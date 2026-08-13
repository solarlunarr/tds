import pygame as pg

class DamageText(pg.sprite.Sprite):
    def __init__(self, x, y, damage, font, color=(255, 50, 50)): # Default to a red color
        pg.sprite.Sprite.__init__(self)
        
        # Add a minus sign for style, e.g., "-15"
        self.image = font.render(f"-{damage}", True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Timer variables to control how long it stays on screen
        self.timer = 0
        self.lifetime = 45 # 45 frames (about 0.75 seconds at 60 FPS)

    def update(self):
        # Float the text upwards
        self.rect.y -= 2 
        
        # Increment timer and delete when lifetime is over
        self.timer += 1
        if self.timer >= self.lifetime:
            self.kill()