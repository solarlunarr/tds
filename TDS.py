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
from turret_data import TURRET_DATA
import sys
import Constants as c

pg.init() #initialise game
vec = pg.math.Vector2
FramePerSecond = pg.time.Clock()
#creates game window and the name of game
screen = pg.display.set_mode((c.WIDTH + c.SIDE_PANEL, c.HEIGHT)) #creates the window you will be playing on

pg.display.set_caption("Prototype TDS")

#game variables
game_over = False
game_outcome = 0 # -1 is a loss/ 1 is a win
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turret = False
selected_turret = None
player_equation = ""
stat_rects = {}#used for clicking on turret stats


#images needed for game --------------------------------------------------------------------------
#load images
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

#load json data for level (waypoints)--------------------------------------------------
with open('tds/assets/Map1.tmj') as file:
    world_data = json.load(file)
#--------------------------------------------------------------------------------
#load font for displaying text on screen
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36)

#--------------------------------------------------------------------------------

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

def display_data():
  #draw panel
  pg.draw.rect(screen, "black", (c.WIDTH, 0, c.SIDE_PANEL, c.HEIGHT))
  pg.draw.rect(screen, "white", (c.WIDTH, 0, c.SIDE_PANEL, 300), 2)
  screen.blit(scaled_logo, (c.WIDTH+80,650))
  #display data
  draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.WIDTH + 10, 10)
  draw_text("Health: " + str(world.health), text_font, "grey100", c.WIDTH + 10, 40)
  draw_text("Money: " + str(world.money), text_font, "grey100", c.WIDTH + 10, 70)


def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    #calculate the number of the tile
    mouse_tile_num = ((mouse_tile_y * c.COLS) + mouse_tile_x)
    #checks to see if that tile is stone of grass
    if world.tile_map[mouse_tile_num] == 3823:
        #checks if there is already a turret there
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x,mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        #if there is space, create turret
        if space_is_free == True:
            new_turret = Turret(IceTurret, mouse_tile_x, mouse_tile_y)
            turret_group.add(new_turret)
            #deduct cost
            world.money -= c.BUY_COST

def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE   
    for turret in turret_group:
        if (mouse_tile_x,mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret

def clear_selection():
    for turret in turret_group:
        turret.selected = False

#---------------------------------------------- drag mechanics
class DraggableOperator:
    def __init__(self, operator, x, y, font):
        self.operator = operator
        self.x = x
        self.y = y
        self.font = font
        self.count = 0  # Starts with 0 available drops
        self.image = None
        self.rect = None
        self.is_dragging = False
        self.original_pos = (x, y)
        self.update_image()

    def update_image(self):
        # Green background if available (>0), Dark Grey if locked (0)
        bg_color = (34, 139, 34) if self.count > 0 else (60, 60, 60)
        text_color = (255, 255, 255)
        
        text_str = f"({self.operator}) x{self.count}"
        self.image = self.font.render(text_str, True, text_color, bg_color)
        
        if self.rect is None:
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
        else:
            if not self.is_dragging:
                self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def add_drop(self):
        self.count += 1
        self.update_image()

    def use_drop(self):
        if self.count > 0:
            self.count -= 1
            self.update_image()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def snap_back(self):
        self.rect.topleft = self.original_pos
        self.update_image()

#----------------------------------------------------------
class Math(pg.sprite.Sprite):
    def __init__(self, x, y, value, font):
        super().__init__()
        self.value = value
        self.image = pg.Surface((35,35))
        self.image.fill((200,200,200))
        pg.draw.rect(self.image, (0,0,0), (0,0,35,35), 2) #black border

        #render the math symbols
        text = font.render(self.value, True, (0,0,0))
        self.image.blit(text, (10,5))
        self.rect = self.image.get_rect(center = (x,y))

#create the world -----------------------------------------------------
world = World(world_data, map_image)
world.process_enemies()
world.process_data()


#creates group---------------------------------------------------------
turret_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
drop_group = pg.sprite.Group()
#creates button--------------------------------------------------
Iceturret_button = Button(c.WIDTH + 30, 120, buy_IceTurret_image, True)
cancel_button = Button(c.WIDTH + 90, 200, scaled_cancel, True)
start_button = Button(c.WIDTH+165, 10,scaled_start, True)
restart_button = Button(550,500, scaled_restart, True)
speed_button = Button(c.WIDTH+165, 15,scaled_speed, False) #require you to hold press it to fast forward
#GUI
logo_image = pg.image.load('tds/assets/logo.webp').convert_alpha()
scaled_logo = pg.transform.scale(logo_image, (125,200))


math_operators = []
op_symbols = ['+', '-', 'x', '/', '^']
start_y = 300 

for i, sym in enumerate(op_symbols):
    new_op = DraggableOperator(sym, c.WIDTH + 30, start_y + (i * 50), text_font)
    math_operators.append(new_op)

run = True
#game loop
while run:
    #drawing section ---------------------------------------------------
    world.draw(screen) #draws the map on the screen
    FramePerSecond.tick(c.FPS) #limits framerate to 60 fps

    if game_over == False:
        if world.health <= 0: #if you lose game over
            game_over = True
            game_outcome = -1
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1
        #update groups
        enemy_group.update(world)
        turret_group.update(enemy_group, world, bullet_image, bullet_group)
        bullet_group.update()

        #bullet hit detection
        hits = pg.sprite.groupcollide(enemy_group, bullet_group, False, True)
        for enemy, bullets_hit in hits.items():
            for bullet in bullets_hit:
                enemy.health -= bullet.damage * len(bullets_hit)
        #Highlight selected turret
        if selected_turret:
            selected_turret.selected = True

        for drop_data in world.pending_drops:
            drop_group.add(Math(drop_data[0], drop_data[1], drop_data[2], text_font))
        world.pending_drops.clear()
    #draw groups ---------------------
    # --------------------------------
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)
    drop_group.draw(screen)
    bullet_group.draw(screen)
    display_data()

    if game_over == False:

        #check if the level has started
        if level_started == False:
            if start_button.draw(screen):
                level_started = True
        else:
            #fast forward option (speed button)
            world.game_speed = 1
            if speed_button.draw(screen):
                world.game_speed = 2
            
            #spawn enemies
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()


        #check if the wave if finished ------------------------------------------
        if world.check_level_complete() == True:
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()

        #draw buttons------------------------------------------------------------------
        #draw the price of a turret
        draw_text(str(c.BUY_COST), text_font, "grey100", c.WIDTH + 35, 200)

        if Iceturret_button.draw(screen):
            placing_turret = True

        #if placing turret, then show cancel button as well
        if placing_turret == True:
            #show cursor turret
            IceTurret_rect = IceTurret.get_rect()
            IceTurret_pos = pg.mouse.get_pos()
            IceTurret_rect.center = IceTurret_pos
            if IceTurret_pos[0] <= c.WIDTH:
                screen.blit(IceTurret, IceTurret_rect)

            if cancel_button.draw(screen):
                placing_turret = False

        #if a turret is selected, show the upgrade button
        if selected_turret:
            pg.draw.rect(screen, "grey", (1200,300,300,350))
            stat_rects.clear() #remove previous frame
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
                #draw the price of a upgrade
                #draw the turret upgrade screen
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.WIDTH + 120, 330)
                upgrade_button = Button(c.WIDTH + 5, 320, scaled_upgrade, True) #upgrade button moved here so it is drawn above the grey background
                if upgrade_button.draw(screen):
                    if world.money >= c.BUY_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST
            else:
                draw_text("Max upgrade", text_font, "black", c.WIDTH + 70, 330)
            #draw the math equation
            draw_text(f"Math: [{player_equation}]", text_font, "white", 1210,430)

            stat_rects['dmg'] = pg.Rect(1210,420,280,40)
            pg.draw.rect(screen, (150, 50, 50), stat_rects['dmg'])
            draw_text(f"+ DMG ({selected_turret.dmg})", text_font, "white", 1220, 430)

            stat_rects['spd'] = pg.Rect(1210, 470, 280, 40)
            pg.draw.rect(screen, (50, 150, 50), stat_rects['spd'])
            draw_text(f"+ SPD ({selected_turret.cooldown})", text_font, "white", 1220, 480)
            
            stat_rects['range'] = pg.Rect(1210, 520, 280, 40)
            pg.draw.rect(screen, (50, 50, 150), stat_rects['range'])
            draw_text(f"+ Range ({selected_turret.range})", text_font, "white", 1220, 530)




    else:
        pg.draw.rect(screen, "blue", (400,300,500,300), border_radius = 30)
        if game_outcome == -1:
            draw_text("Game Over", large_font, "grey", 550, 400)
        elif game_outcome == 1:
            draw_text("You have finished our demo!", large_font, "grey", 400, 400)

        #restart level
        if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turret = False
            selected_turret = False
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()

            #empty groups
            enemy_group.empty()
            turret_group.empty()
            pass

    # Handle events -----------------------------------------------------------
    for event in pg.event.get():
        if event.type == QUIT: #allows you to click exit to exit
            pg.quit()
            sys.exit()

        #mouse clicks to place down turrets
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
        #check if mouse is in game area
            if mouse_pos[0] < c.WIDTH and mouse_pos[1] < c.HEIGHT:
                selected_turret = None
                clear_selection()
                if placing_turret == True:
                    #check if there is enough gold for turret
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)

#  # Handle dragging position
#         if event.type == pg.MOUSEMOTION:
#             for op in math_operators:
#                 if op.is_dragging:
#                     op.rect.center = event.pos

#         # Handle dropping operator onto turret
#         if event.type == pg.MOUSEBUTTONUP and event.button == 1:
#             for op in math_operators:
#                 if op.is_dragging:
#                     op.is_dragging = False
#                     mouse_pos = pg.mouse.get_pos()
#                     mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
#                     mouse_tile_y = mouse_pos[1] // c.TILE_SIZE 
                    
#                     for turret in turret_group:
#                         if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
#                             turret.apply_math(op.operator)
#                             op.use_drop() # Deducts 1 drop & updates green state
#                             break
#                     op.snap_back()

#         # Handle mouse press
#         if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
#             mouse_pos = pg.mouse.get_pos()
            
#             clicked_operator = False
#             for op in math_operators:
#                 # ONLY allow dragging if count > 0!
#                 if op.rect.collidepoint(mouse_pos) and op.count > 0:
#                     op.is_dragging = True
#                     clicked_operator = True
#                     break
            
#             if not clicked_operator:
#                 if mouse_pos[0] < c.WIDTH and mouse_pos[1] < c.HEIGHT:
#                     selected_turret = None
#                     clear_selection()
#                     if placing_turret == True:
#                         if world.money >= c.BUY_COST:
#                             create_turret(mouse_pos)
#                     else:
#                         selected_turret = select_turret(mouse_pos)

#     for op in math_operators:
#         op.draw(screen)
    #updates display -------------------------------------------------------
    pg.display.update()