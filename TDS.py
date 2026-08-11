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
import sys
import Constants as c

pg.init() #initialise game
vec = pg.math.Vector2
FramePerSecond = pg.time.Clock()
windowsize=pg.display.get_desktop_sizes

#creates game window and the name of game
screen = pg.display.set_mode((c.WIDTH+c.SIDE_PANEL, c.HEIGHT)) #creates the window you will be playing on
# pg.display.toggle_fullscreen()
pg.display.set_caption("Prototype TDS")

#game variables
game_over = False
game_outcome = 0 # -1 is a loss/ 1 is a win
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turret = False
selected_turret = None




#images needed for game --------------------------------------------------------------------------
#load images
map_image = pg.image.load('tds/assets/Map1.png').convert_alpha()
enemy_images = {
    "weak": pg.image.load('tds/assets/enemy.png').convert_alpha(),
    "strong": pg.image.load('tds/assets/enemy2.png').convert_alpha()
}

IceTurret = pg.image.load('tds/assets/IceTurret.png').convert_alpha()
buy_turret_image = pg.image.load('tds/assets/IceTurret.png').convert_alpha()
cancel_image = pg.image.load('tds/assets/Cancel.png').convert_alpha()
upgrade_image = pg.image.load('tds/assets/Upgrade.png').convert_alpha()
start_image = pg.image.load('tds/assets/Start.png').convert_alpha()
restart_image = pg.image.load('tds/assets/Restart.png').convert_alpha()
bullet_image = pg.image.load('tds/assets/Bullet.png').convert_alpha()


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
# ---------------------------



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

#create the world -----------------------------------------------------
world = World(world_data, map_image)
world.process_enemies()
world.process_data()


#creates group---------------------------------------------------------
turret_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()

#creates button--------------------------------------------------
turret_button = Button(c.WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.WIDTH + 80, 180, cancel_image, True)
upgrade_button = Button(c.WIDTH + 5, 200, upgrade_image, True )
start_button = Button(c.WIDTH+10, 10,start_image, True)
restart_button = Button(550,500, restart_image, True)

math_operators = []
op_symbols = ['+', '-', 'x', '/', '^']
start_y = 300 

for i, sym in enumerate(op_symbols):
    new_op = DraggableOperator(sym, c.WIDTH + 30, start_y + (i * 50), text_font)
    math_operators.append(new_op)

run = True
#game loop
while run:
    screen.fill("black")
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
        enemy_group.update(world,math_operators)
        turret_group.update(enemy_group, bullet_group, bullet_image)
        bullet_group.update()

        # bullet hit detection
        hits = pg.sprite.groupcollide(enemy_group, bullet_group, False, True)
        for enemy, bullets_hit in hits.items():
            enemy.health -= c.DAMAGE * len(bullets_hit)
        #Highlight selected turret
        if selected_turret:
            selected_turret.selected = True

    #draw groups -----------------------------------------------------
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)
        bullet_group.draw(screen)

    draw_text( str(world.health), text_font, "grey", 1400,0) #shows your health
    draw_text( str(world.money), text_font, "grey", 1400,30) #shows your money
    draw_text( str(world.level), text_font, "grey", 1400,60) #shows your current round level

    if game_over == False:

        #check if the level has started
        if level_started == False:
            if start_button.draw(screen):
                level_started = True
        else:
            #spawn enemies
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()


        #check if the wave if finifshed ------------------------------------------
        if world.check_level_complete() == True:
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()

        #draw buttons------------------------------------------------------------------
        if turret_button.draw(screen):
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
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
                if upgrade_button.draw(screen):
                    if world.money >= c.BUY_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST

    else:
        pg.draw.rect(screen, "blue", (400,300,500,300), border_radius = 30)
        if game_outcome == -1:
            draw_text("Game Over", large_font, "grey", 310, 230)
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
            bullet_group.empty()
            pass


   # Handle events -----------------------------------------------------------
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()

        # Handle dragging position
        if event.type == pg.MOUSEMOTION:
            for op in math_operators:
                if op.is_dragging:
                    op.rect.center = event.pos

        # Handle dropping operator onto turret
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for op in math_operators:
                if op.is_dragging:
                    op.is_dragging = False
                    mouse_pos = pg.mouse.get_pos()
                    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
                    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE 
                    
                    for turret in turret_group:
                        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                            turret.apply_math(op.operator)
                            op.use_drop() # Deducts 1 drop & updates green state
                            break
                    op.snap_back()

        # Handle mouse press
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            
            clicked_operator = False
            for op in math_operators:
                # ONLY allow dragging if count > 0!
                if op.rect.collidepoint(mouse_pos) and op.count > 0:
                    op.is_dragging = True
                    clicked_operator = True
                    break
            
            if not clicked_operator:
                if mouse_pos[0] < c.WIDTH and mouse_pos[1] < c.HEIGHT:
                    selected_turret = None
                    clear_selection()
                    if placing_turret == True:
                        if world.money >= c.BUY_COST:
                            create_turret(mouse_pos)
                    else:
                        selected_turret = select_turret(mouse_pos)

    for op in math_operators:
        op.draw(screen)
    #updates display -------------------------------------------------------
    pg.display.update()



    #baiyi yus edit
    