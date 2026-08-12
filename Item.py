import pygame as pg
import random
import Constants as c

OPERATORS = ['+', 'x', '-', '/', '^']

class Item:
    def __init__(self, op_type=None):
        self.op_type = op_type if op_type else random.choice(OPERATORS)
        self.value = self.generate_value()
        self.is_dragging = False
        self.is_selected = False
        self.rect = pg.Rect(0, 0, 45, 45)
        self.font = pg.font.SysFont("Consolas", 18, bold=True)

    def generate_value(self):
        if self.op_type == '+':
            return random.randint(3, 10)         # Flat damage boost
        elif self.op_type == 'x':
            return round(random.uniform(1.5, 2.5), 1) # Damage multiplier
        elif self.op_type == '-':
            return random.randint(15, 40)        # Direct damage to enemy
        elif self.op_type == '/':
            return 0.5                           # Halves enemy speed
        elif self.op_type == '^':
            return round(random.uniform(1.2, 1.5), 2) # Exponent power
        return 1

    def get_text(self):
        if self.op_type == '/':
            return "/2"
        return f"{self.op_type}{self.value}"

    def draw(self, surface, pos=None):
        draw_rect = self.rect if pos is None else pg.Rect(pos[0] - 22, pos[1] - 22, 45, 45)
        
        colors = {
            '+': (40, 160, 220),   # Light Blue
            'x': (220, 160, 40),   # Orange
            '-': (220, 60, 60),    # Red
            '/': (160, 60, 220),   # Purple
            '^': (60, 220, 100)    # Green
        }
        bg_color = colors.get(self.op_type, (100, 100, 100))
        
        pg.draw.rect(surface, bg_color, draw_rect, border_radius=6)
        border_color = "yellow" if self.is_selected else "white"
        border_width = 3 if self.is_selected else 2
        pg.draw.rect(surface, border_color, draw_rect, width=border_width, border_radius=6)
        
        txt_surf = self.font.render(self.get_text(), True, "white")
        txt_rect = txt_surf.get_rect(center=draw_rect.center)
        surface.blit(txt_surf, txt_rect)


class Inventory:
    def __init__(self, x, y, slots=6):
        self.x = x
        self.y = y
        self.slots = [None] * slots

    def add_item(self, item):
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = item
                item.rect.topleft = (self.x + (i % 3) * 55, self.y + (i // 3) * 55)
                return True
        return False

    def draw(self, surface):
        font = pg.font.SysFont("Consolas", 18, bold=True)
        title = font.render("OPERATIONS", True, "white")
        surface.blit(title, (self.x, self.y - 25))

        for i in range(len(self.slots)):
            slot_x = self.x + (i % 3) * 55
            slot_y = self.y + (i // 3) * 55
            slot_rect = pg.Rect(slot_x, slot_y, 48, 48)
            
            pg.draw.rect(surface, (40, 40, 40), slot_rect, border_radius=6)
            pg.draw.rect(surface, (80, 80, 80), slot_rect, width=2, border_radius=6)

            item = self.slots[i]
            if item and not item.is_dragging:
                item.rect.topleft = (slot_x + 1, slot_y + 1)
                item.draw(surface)