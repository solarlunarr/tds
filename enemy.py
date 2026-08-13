# enemy.py
import pygame as pg
from pygame.math import Vector2
import math
import random
from enemy_data import ENEMY_DATA
import Constants as c

class BossArrow(pg.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        pg.sprite.Sprite.__init__(self)
        self.pos = Vector2(start_pos)
        self.target = Vector2(target_pos)
        self.speed = 14
        self.damage_dealt = False
        
        diff = self.target - self.pos
        self.direction = diff.normalize() if diff.length() > 0 else Vector2(1, 0)
        
        # Red/Orange glowing arrow graphic
        self.image = pg.Surface((36, 10), pg.SRCALPHA)
        pg.draw.polygon(self.image, (255, 40, 0), [(0, 0), (36, 5), (0, 10)])
        pg.draw.polygon(self.image, (255, 220, 0), [(6, 3), (30, 5), (6, 7)])
        
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.image = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, world):
        dist = (self.target - self.pos).length()
        if dist <= self.speed:
            if not self.damage_dealt:
                world.health -= int(c.HEALTH * 0.5)  # Deals 50% of base Max HP
                self.damage_dealt = True
            self.kill()
        else:
            self.pos += self.direction * self.speed
            self.rect.center = self.pos


class Enemy(pg.sprite.Sprite):
    def __init__(self, enemy_type, waypoints, images, turret_group=None):
        pg.sprite.Sprite.__init__(self)
        data = ENEMY_DATA.get(enemy_type)
        self.enemy_type = enemy_type
        self.waypoints = waypoints
        self.turret_group = turret_group
        self.pos = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.health = data["health"]
        self.max_health = data["health"]

        # HP scaling
        if self.turret_group and len(self.turret_group) > 0:
            max_turret_damage = max(t.damage for t in self.turret_group)
            THRESHOLD_PCT = 2
            if self.enemy_type != "boss":
                if max_turret_damage > (self.max_health * THRESHOLD_PCT):
                    scaled_health = int(max_turret_damage / (THRESHOLD_PCT/4))
                    self.health = scaled_health
                    self.max_health = scaled_health

        self.speed = data["speed"]
        self.armor = data.get("armor", 0)
        self.regen = data.get("regen", 0)
        self.base_damage = data.get("damage", 25)
        self.reward = data.get("reward", c.KILL_REWARD)
        self.angle = 0
        self.original_image = images.get(enemy_type)
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        # Boss Enrage & Shockwave State
        self.enraged = False
        self.shockwave_active = False
        self.shockwave_radius = 0
        self.shockwave_max_radius = 600

        # Boss Death Animation State
        self.dying = False
        self.death_timer = 0
        self.max_death_time = 120  # ~2 seconds at 60 FPS
        self.explosions = []
        self.saved_inventory = None

    def trigger_enrage(self, world, enemy_group=None, enemy_images=None, boss_arrow_group=None):
        """Triggers shockwave, stuns turrets, doubles speed, shoots base arrow, and spawns minions."""
        self.enraged = True
        self.speed *= 2.0  # Double boss speed
        self.shockwave_active = True
        self.shockwave_radius = 10

        # 1. Stun all turrets for 3.5 seconds
        if self.turret_group:
            stun_duration = pg.time.get_ticks() + 3500
            for turret in self.turret_group:
                turret.stunned_until = stun_duration

        # 2. Launch Arrow at Base (Deals 50% max base health)
        base_position = self.waypoints[-1]
        if boss_arrow_group is not None:
            boss_arrow_group.add(BossArrow(self.pos, base_position))
        else:
            world.health -= int(c.HEALTH * 0.5)

        # 3. Spawn Reinforcement Minions at Boss Location
        if enemy_group is not None and enemy_images is not None:
            minion_types = ["strong", "weak", "strong", "weak"]
            for m_type in minion_types:
                minion = Enemy(m_type, self.waypoints, enemy_images, self.turret_group)
                minion.pos = Vector2(self.pos.x + random.randint(-25, 25), self.pos.y + random.randint(-25, 25))
                minion.target_waypoint = self.target_waypoint
                enemy_group.add(minion)

    def update(self, world):
        if self.dying:
            self.update_death_animation(world)
            return

        self.move(world)
        if self.alive():
            self.rotate()
            self.regenerate(world)

            # Expand Shockwave Ring
            if self.shockwave_active:
                self.shockwave_radius += 12 * world.game_speed
                if self.shockwave_radius >= self.shockwave_max_radius:
                    self.shockwave_active = False

    def update_death_animation(self, world):
        """Animates shaking, spinning, scaling down, and popping particle bursts on boss death."""
        self.death_timer -= 1 * world.game_speed

        # Spawn random explosion rings across boss body
        if random.random() < 0.45:
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-40, 40)
            self.explosions.append({
                'x': self.pos.x + offset_x,
                'y': self.pos.y + offset_y,
                'radius': 4,
                'max_radius': random.randint(20, 45),
                'color': random.choice([(255, 60, 0), (255, 220, 0), (255, 255, 255), (200, 30, 30)])
            })

        # Update existing explosion particles
        for exp in self.explosions[:]:
            exp['radius'] += 3 * world.game_speed
            if exp['radius'] >= exp['max_radius']:
                self.explosions.remove(exp)

        # Boss Spin, Shake, and Shrink
        progress = max(0.01, self.death_timer / self.max_death_time)
        scaled_w = max(1, int(90 * progress))
        scaled_h = max(1, int(90 * progress))
        
        # Shake offset
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-5, 5)

        self.angle += 8 * world.game_speed  # Rapid spin
        scaled_img = pg.transform.scale(self.original_image, (scaled_w, scaled_h))
        self.image = pg.transform.rotate(scaled_img, self.angle)
        self.rect = self.image.get_rect(center=(self.pos.x + shake_x, self.pos.y + shake_y))

        # Final death completion
        if self.death_timer <= 0:
            world.killed_enemies += 1
            world.money += self.reward
            
            if self.saved_inventory and random.random() < 0.35:
                from Item import Item
                self.saved_inventory.add_item(Item(current_level=world.level))
                
            self.kill()

    def take_damage(self, amount, world=None, enemy_group=None, enemy_images=None, boss_arrow_group=None):
        if self.dying:
            return  # Immune to hits while executing death animation

        reduced = amount * (1 - self.armor)
        self.health -= reduced

        # Boss Enrage Trigger at <= 10% Health
        if self.enemy_type == "boss" and not self.enraged and self.health <= (self.max_health * 0.10) and self.health > 0:
            self.trigger_enrage(world, enemy_group, enemy_images, boss_arrow_group)

    def regenerate(self, world):
        if self.regen > 0 and self.health < self.max_health:
            self.health = min(self.max_health, self.health + (self.regen * world.game_speed))

    def draw_health_bar(self, surface):
        if self.dying:
            # Render death explosion particles
            for exp in self.explosions:
                pg.draw.circle(surface, exp['color'], (int(exp['x']), int(exp['y'])), int(exp['radius']), 3)

            # Detonate large shockwave burst in final frames
            if self.death_timer < 35:
                shockwave_r = int((35 - self.death_timer) * 14)
                pg.draw.circle(surface, (255, 215, 0), (int(self.pos.x), int(self.pos.y)), shockwave_r, 5)
                pg.draw.circle(surface, (255, 60, 0), (int(self.pos.x), int(self.pos.y)), max(1, shockwave_r - 12), 3)
            return

        if self.shockwave_active:
            pg.draw.circle(surface, (255, 60, 0), (int(self.pos.x), int(self.pos.y)), int(self.shockwave_radius), 6)
            pg.draw.circle(surface, (255, 215, 0), (int(self.pos.x), int(self.pos.y)), max(1, int(self.shockwave_radius - 8)), 2)

        bar_width = 60
        bar_height = 8
        fill_pct = max(0, self.health / self.max_health)
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 16
        
        bar_color = (255, 120, 0) if self.enraged else (200, 30, 30)

        pg.draw.rect(surface, (60, 0, 0), (x, y, bar_width, bar_height))
        pg.draw.rect(surface, bar_color, (x, y, int(bar_width * fill_pct), bar_height))
        pg.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 1)

    def move(self, world):
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            self.kill()
            world.health -= self.base_damage
            world.missed_enemies += 1
            return

        dist = self.movement.length()
        if dist >= (self.speed * world.game_speed):
            self.pos += self.movement.normalize() * (self.speed * world.game_speed)
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

    def rotate(self):
        dist = self.target - self.pos
        self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def check_alive(self, world, inventory=None):
        if self.health <= 0:
            if self.enemy_type == "boss" and not self.dying:
                self.dying = True
                self.death_timer = self.max_death_time
                self.saved_inventory = inventory
                self.shockwave_active = False  # Cancel any active enrage wave
            elif not self.dying:
                world.killed_enemies += 1
                world.money += self.reward
                
                if inventory and random.random() < 0.35:
                    from Item import Item
                    inventory.add_item(Item(current_level=world.level))
                    
                self.kill()