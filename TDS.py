# TDS.py
'''
Massive thanks to Coding with Russ's video https://youtu.be/WRuf9iPAXfM?si=EzAuJXg-UUN4lpym 
'''

import pygame as pg
import json
from pygame.locals import *
from turret import Turret
from enemy import Enemy
from world import World
from button import Button
from Item import Inventory
import sys
import Constants as c

pg.init()
FramePerSecond = pg.time.Clock()
screen = pg.display.set_mode((c.WIDTH + c.SIDE_PANEL, c.HEIGHT))
pg.display.set_caption("Prototype TDS")

# Game variables
game_over = False
game_outcome = 0
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turret = False
selected_turret = None

# Targeting state for Division (/) and Subtraction (-)
targeting_item = None
targeting_slot_index = None

# Images
map_image = pg.image.load('tds/assets/map2.png').convert_alpha()
enemy_images = {
    "weak": pg.image.load('tds/assets/slime.png').convert_alpha(),
    "strong": pg.image.load('tds/assets/enemy2.png').convert_alpha()
}

# Load Boss Asset
try:
    boss_image = pg.image.load('tds/assets/boss.png').convert_alpha()
except:
    boss_image = pg.image.load('tds/assets/boss.png').convert_alpha()
boss_image = pg.transform.rotate(boss_image, 90)
boss_image = pg.transform.scale(boss_image, (90, 90))
enemy_images["boss"] = boss_image

IceTurret = pg.image.load('tds/assets/IceTurret.png').convert_alpha()
buy_IceTurret_image = pg.image.load('tds/assets/IceTurret.png').convert_alpha()
cancel_image = pg.image.load('tds/assets/Cancel.png').convert_alpha()
scaled_cancel = pg.transform.scale(cancel_image, (30, 30))
upgrade_image = pg.image.load('tds/assets/Upgrade.png').convert_alpha()
scaled_upgrade = pg.transform.scale(upgrade_image, (100, 30))
start_image = pg.image.load('tds/assets/Start.png').convert_alpha()
scaled_start = pg.transform.scale(start_image, (125, 40))
restart_image = pg.image.load('tds/assets/Restart.png').convert_alpha()
scaled_restart = pg.transform.scale(restart_image, (100, 35))
bullet_image = pg.image.load('tds/assets/Bullet.png').convert_alpha()
speed_image = pg.image.load('tds/assets/Speed.png').convert_alpha()
scaled_speed = pg.transform.scale(speed_image, (125, 40))

# Create Sell Button Image (with dynamic fallback if asset missing)
try:
    sell_image = pg.image.load('tds/assets/Sell.png').convert_alpha()
    scaled_sell = pg.transform.scale(sell_image, (100, 30))
except:
    scaled_sell = pg.Surface((100, 30), pg.SRCALPHA)
    pg.draw.rect(scaled_sell, (180, 40, 40), (0, 0, 100, 30), border_radius=6)
    pg.draw.rect(scaled_sell, (240, 80, 80), (0, 0, 100, 30), width=2, border_radius=6)
    btn_font = pg.font.SysFont("Consolas", 14, bold=True)
    txt = btn_font.render("SELL", True, (255, 255, 255))
    scaled_sell.blit(txt, txt.get_rect(center=(50, 15)))

logo_image = pg.image.load('tds/assets/logo.webp').convert_alpha()
scaled_logo = pg.transform.scale(logo_image, (120, 180))

with open('tds/assets/map2.tmj') as file:
    world_data = json.load(file)

text_font = pg.font.SysFont("Consolas", 16, bold=True)
large_font = pg.font.SysFont("Consolas", 36, bold=True)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def display_data():
    # Side Panel Base
    pg.draw.rect(screen, (20, 20, 20), (c.WIDTH, 0, c.SIDE_PANEL, c.HEIGHT))
    pg.draw.line(screen, (60, 60, 60), (c.WIDTH, 0), (c.WIDTH, c.HEIGHT), 3)

    # 1. Top Stats Box
    pg.draw.rect(screen, (35, 35, 35), (c.WIDTH + 10, 10, 135, 65), border_radius=6)
    pg.draw.rect(screen, (80, 80, 80), (c.WIDTH + 10, 10, 135, 65), width=1, border_radius=6)
    draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.WIDTH + 18, 14)
    draw_text("Health: " + str(world.health), text_font, (240, 80, 80), c.WIDTH + 18, 33)
    draw_text("Money: " + str(world.money), text_font, (80, 220, 120), c.WIDTH + 18, 52)

    if getattr(world, "boss_incoming", False):
        draw_text("BOSS WAVE!", text_font, "red", c.WIDTH + 160, 58)

    # 2. Main Action Card (Turret Info / Shop)
    pg.draw.rect(screen, (30, 30, 30), (c.WIDTH + 10, 85, c.SIDE_PANEL - 20, 180), border_radius=8)

    if selected_turret:
        pg.draw.rect(screen, "yellow", (c.WIDTH + 10, 85, c.SIDE_PANEL - 20, 180), width=1, border_radius=8)
        draw_text(f"TURRET LVL {selected_turret.upgrade_level}", text_font, "yellow", c.WIDTH + 20, 93)
        draw_text(f"Damage:   {selected_turret.damage}", text_font, "white", c.WIDTH + 20, 118)
        draw_text(f"Cooldown: {selected_turret.cooldown}ms", text_font, "white", c.WIDTH + 20, 138)
        draw_text(f"Range:    {selected_turret.range}", text_font, "white", c.WIDTH + 20, 158)
    else:
        pg.draw.rect(screen, (70, 70, 70), (c.WIDTH + 10, 85, c.SIDE_PANEL - 20, 180), width=1, border_radius=8)
        draw_text("BUILD / SHOP", text_font, (100, 200, 255), c.WIDTH + 20, 93)
        draw_text("Ice Turret", text_font, "white", c.WIDTH + 80, 122)
        draw_text(f"Cost: ${c.BUY_COST}", text_font, (80, 220, 120), c.WIDTH + 80, 145)

    # Bottom Logo
    screen.blit(scaled_logo, (c.WIDTH + (c.SIDE_PANEL - 120) // 2, 700))

def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    mouse_tile_num = ((mouse_tile_y * c.COLS) + mouse_tile_x)
    if world.tile_map[mouse_tile_num] != 482:
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        if space_is_free:
            new_turret = Turret(IceTurret, mouse_tile_x, mouse_tile_y)
            turret_group.add(new_turret)
            world.money -= c.BUY_COST

def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE   
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret

def clear_selection():
    for turret in turret_group:
        turret.selected = False

world = World(world_data, map_image)
world.process_enemies()
world.process_data()

# Groups & Inventory (Centered inside 300px side panel)
turret_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
inventory = Inventory(c.WIDTH + 40, 295, slots=12, cols=4)

# Buttons
turret_button = Button(c.WIDTH + 25, 120, buy_IceTurret_image, True)
cancel_button = Button(c.WIDTH + 230, 185, scaled_cancel, True)
upgrade_button = Button(c.WIDTH + 25, 190, scaled_upgrade, True)
sell_button = Button(c.WIDTH + 160, 190, scaled_sell, True)

start_button = Button(c.WIDTH + 160, 12, scaled_start, True)
restart_button = Button(560, 490, scaled_restart, True)
speed_button = Button(c.WIDTH + 160, 12, scaled_speed, False)

dragged_item = None
drag_source_index = None

run = True
while run:
    world.draw(screen)
    FramePerSecond.tick(c.FPS)

    if not game_over:
        if world.health <= 0:
            game_over = True
            game_outcome = -1
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1

        enemy_group.update(world)
        turret_group.update(enemy_group, world, bullet_image, bullet_group)
        bullet_group.update()

        hits = pg.sprite.groupcollide(enemy_group, bullet_group, False, True)
        for enemy, bullets_hit in hits.items():
            for bullet in bullets_hit:
                enemy.take_damage(bullet.damage)
            enemy.check_alive(world, inventory)

        if selected_turret:
            selected_turret.selected = True

    # Draw game objects
    enemy_group.draw(screen)
    for enemy in enemy_group:
        if getattr(enemy, "enemy_type", None) == "boss" or enemy.regen > 0:
            enemy.draw_health_bar(screen)

    for turret in turret_group:
        turret.draw(screen)
    bullet_group.draw(screen)

    display_data()
    inventory.draw(screen)

    if not game_over:
        if not level_started:
            if start_button.draw(screen):
                level_started = True
        else:
            world.game_speed = 1
            if speed_button.draw(screen):
                world.game_speed = 2
            
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images, turret_group)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        if world.check_level_complete():
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()

        # UI Actions for Selected Turret or Shop
        if selected_turret:
            # Calculate 50% refund on total invested cost
            sell_refund = int((c.BUY_COST + (selected_turret.upgrade_level - 1) * c.UPGRADE_COST) * 0.5)

            # Upgrade Button
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
                draw_text(f"${c.UPGRADE_COST}", text_font, (80, 220, 120), c.WIDTH + 45, 225)
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST

            # Sell Button
            draw_text(f"+${sell_refund}", text_font, (80, 220, 120), c.WIDTH + 175, 225)
            if sell_button.draw(screen):
                world.money += sell_refund
                selected_turret.kill()
                selected_turret = None
        else:
            # Shop / Placement Mode
            if turret_button.draw(screen):
                placing_turret = True

            if placing_turret:
                IceTurret_rect = IceTurret.get_rect()
                IceTurret_pos = pg.mouse.get_pos()
                IceTurret_rect.center = IceTurret_pos
                if IceTurret_pos[0] <= c.WIDTH:
                    screen.blit(IceTurret, IceTurret_rect)

                draw_text("Placing...", text_font, "yellow", c.WIDTH + 20, 190)
                if cancel_button.draw(screen):
                    placing_turret = False

    else:
        pg.draw.rect(screen, (30, 30, 80), (400, 300, 500, 250), border_radius=20)
        pg.draw.rect(screen, "white", (400, 300, 500, 250), width=2, border_radius=20)
        if game_outcome == -1:
            draw_text("GAME OVER", large_font, (240, 80, 80), 550, 380)
        elif game_outcome == 1:
            draw_text("DEMO COMPLETED", large_font, (80, 220, 120), 500, 360)
            draw_text("Thank you for playing!", large_font, (80, 220, 120), 440, 390)
        if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turret = False
            selected_turret = None
            targeting_item = None
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()
            enemy_group.empty()
            turret_group.empty()
            bullet_group.empty()
            inventory.restart()
    if dragged_item:
        dragged_item.draw(screen, pos=pg.mouse.get_pos())

    if targeting_item:
        mouse_p = pg.mouse.get_pos()
        pg.draw.circle(screen, "red", mouse_p, 15, 2)
        draw_text("SELECT ENEMY", text_font, "red", mouse_p[0] - 50, mouse_p[1] - 30)

    # Event Handling
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()

            # 1. APPLY TARGETED ENEMY OPERATION (- or /)
            if targeting_item:
                target_hit = False
                for enemy in enemy_group:
                    if enemy.rect.collidepoint(mouse_pos):
                        if targeting_item.op_type == '-':
                            enemy.take_damage(targeting_item.value)
                            enemy.check_alive(world, inventory)
                        elif targeting_item.op_type == '/':
                            enemy.speed = max(0.5, enemy.speed * targeting_item.value)
                        
                        target_hit = True
                        break

                if target_hit:
                    inventory.slots[targeting_slot_index] = None

                if targeting_item:
                    targeting_item.is_selected = False
                targeting_item = None
                targeting_slot_index = None

            else:
                # 2. CLICK INVENTORY ITEM
                clicked_inventory = False
                for i, item in enumerate(inventory.slots):
                    if item and item.rect.collidepoint(mouse_pos):
                        clicked_inventory = True
                        if item.op_type in ['-', '/']:
                            targeting_item = item
                            targeting_slot_index = i
                            item.is_selected = True
                        else:
                            dragged_item = item
                            drag_source_index = i
                            item.is_dragging = True
                        break

                # 3. SELECT OR PLACE TURRET
                if not clicked_inventory and mouse_pos[0] < c.WIDTH and mouse_pos[1] < c.HEIGHT:
                    selected_turret = None
                    clear_selection()
                    if placing_turret:
                        if world.money >= c.BUY_COST:
                            create_turret(mouse_pos)
                    else:
                        selected_turret = select_turret(mouse_pos)

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if dragged_item:
                mouse_pos = pg.mouse.get_pos()
                applied = False

                for turret in turret_group:
                    if turret.rect.collidepoint(mouse_pos):
                        turret.apply_item(dragged_item)
                        applied = True
                        break

                if applied:
                    inventory.slots[drag_source_index] = None

                dragged_item.is_dragging = False
                dragged_item = None
                drag_source_index = None

    pg.display.update()