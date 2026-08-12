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
map_image = pg.image.load('tds/assets/Map1.png').convert_alpha()
enemy_images = {
    "weak": pg.image.load('tds/assets/enemy.png').convert_alpha(),
    "strong": pg.image.load('tds/assets/enemy2.png').convert_alpha()
}

IceTurret = pg.image.load('tds/assets/IceTurret.png').convert_alpha()
buy_IceTurret_image = pg.image.load('tds/assets/IceTurret.png').convert_alpha()
cancel_image = pg.image.load('tds/assets/Cancel.png').convert_alpha()
scaled_cancel = pg.transform.scale(cancel_image, (30,30))
upgrade_image = pg.image.load('tds/assets/Upgrade.png').convert_alpha()
scaled_upgrade = pg.transform.scale(upgrade_image, (100,30))
start_image = pg.image.load('tds/assets/Start.png').convert_alpha()
scaled_start = pg.transform.scale(start_image, (125,50))
restart_image = pg.image.load('tds/assets/Restart.png').convert_alpha()
scaled_restart = pg.transform.scale(restart_image, (75,30))
bullet_image = pg.image.load('tds/assets/Bullet.png').convert_alpha()
speed_image = pg.image.load('tds/assets/Speed.png').convert_alpha()
scaled_speed = pg.transform.scale(speed_image, (125,50))

with open('tds/assets/Map1.tmj') as file:
    world_data = json.load(file)

text_font = pg.font.SysFont("Consolas", 20, bold=True)
large_font = pg.font.SysFont("Consolas", 36)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def display_data():
    pg.draw.rect(screen, "black", (c.WIDTH, 0, c.SIDE_PANEL, c.HEIGHT))
    pg.draw.rect(screen, "white", (c.WIDTH, 0, c.SIDE_PANEL, 300), 2)
    screen.blit(scaled_logo, (c.WIDTH + 80, 650))
    
    # Base Stats
    draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.WIDTH + 10, 10)
    draw_text("Health: " + str(world.health), text_font, "grey100", c.WIDTH + 10, 35)
    draw_text("Money: " + str(world.money), text_font, "grey100", c.WIDTH + 10, 60)

    # Turret Info / Upgrade Menu Display
    if selected_turret:
        pg.draw.rect(screen, (30, 30, 30), (c.WIDTH + 5, 90, c.SIDE_PANEL - 10, 110), border_radius=6)
        pg.draw.rect(screen, "yellow", (c.WIDTH + 5, 90, c.SIDE_PANEL - 10, 110), width=1, border_radius=6)
        
        draw_text(f"TURRET LVL {selected_turret.upgrade_level}", text_font, "yellow", c.WIDTH + 15, 95)
        draw_text(f"Damage: {selected_turret.damage}", text_font, "white", c.WIDTH + 15, 120)
        draw_text(f"Cooldown: {selected_turret.cooldown}ms", text_font, "white", c.WIDTH + 15, 145)
        draw_text(f"Range: {selected_turret.range}", text_font, "white", c.WIDTH + 15, 170)

def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    mouse_tile_num = ((mouse_tile_y * c.COLS) + mouse_tile_x)
    if world.tile_map[mouse_tile_num] == 3823:
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

# Groups & Inventory
turret_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
inventory = Inventory(c.WIDTH + 15, 330, slots=6)

# Buttons
turret_button = Button(c.WIDTH + 30, 210, buy_IceTurret_image, True)
cancel_button = Button(c.WIDTH + 90, 250, scaled_cancel, True)
start_button = Button(c.WIDTH + 175, 10, scaled_start, True)
restart_button = Button(550, 500, scaled_restart, True)
speed_button = Button(c.WIDTH + 175, 40, scaled_speed, False)

logo_image = pg.image.load('tds/assets/logo.webp').convert_alpha()
scaled_logo = pg.transform.scale(logo_image, (125, 200))

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

        # Bullet collision
        hits = pg.sprite.groupcollide(enemy_group, bullet_group, False, True)
        for enemy, bullets_hit in hits.items():
            for bullet in bullets_hit:
                enemy.health -= bullet.damage
            enemy.check_alive(world, inventory)

        if selected_turret:
            selected_turret.selected = True

    # Draw game objects
    enemy_group.draw(screen)
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
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
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

        draw_text(str(c.BUY_COST), text_font, "grey100", c.WIDTH + 35, 250)

        if turret_button.draw(screen):
            placing_turret = True

        if placing_turret:
            IceTurret_rect = IceTurret.get_rect()
            IceTurret_pos = pg.mouse.get_pos()
            IceTurret_rect.center = IceTurret_pos
            if IceTurret_pos[0] <= c.WIDTH:
                screen.blit(IceTurret, IceTurret_rect)

            if cancel_button.draw(screen):
                placing_turret = False

        if selected_turret and selected_turret.upgrade_level < c.TURRET_LEVELS:
            draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.WIDTH + 110, 270)
            upgrade_button = Button(c.WIDTH + 175, 240, scaled_upgrade, False)
            if upgrade_button.draw(screen):
                if world.money >= c.UPGRADE_COST:
                    selected_turret.upgrade()
                    world.money -= c.UPGRADE_COST

    else:
        pg.draw.rect(screen, "blue", (400, 300, 500, 300), border_radius=30)
        if game_outcome == -1:
            draw_text("Game Over", large_font, "grey", 550, 400)
        elif game_outcome == 1:
            draw_text("You have finished our demo!", large_font, "grey", 400, 400)

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

    # Drag preview for tower items (+, x, ^)
    if dragged_item:
        dragged_item.draw(screen, pos=pg.mouse.get_pos())

    # Target indicator for enemy items (- and /)
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
                            enemy.health -= targeting_item.value
                            enemy.check_alive(world, inventory)
                        elif targeting_item.op_type == '/':
                            enemy.speed = max(0.5, enemy.speed * targeting_item.value)
                        
                        target_hit = True
                        break

                if target_hit:
                    # Consume item after successful use
                    inventory.slots[targeting_slot_index] = None

                # Cancel targeting mode
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
                            # Enter targeting mode
                            targeting_item = item
                            targeting_slot_index = i
                            item.is_selected = True
                        else:
                            # Start drag mode for tower upgrades (+, x, ^)
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

                # Drop consumable upgrade on existing turret (+, x, ^)
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