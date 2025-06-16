#! /usr/bin/env python
import pygame
import py_trees
import random as Random
from pygame.locals import *
from sys import exit


pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100, 32, 2, 4096)

font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 72)
info_font = pygame.font.SysFont(font_name, 24)
menu_font = pygame.font.SysFont(font_name, 36)

screen = pygame.display.set_mode((448,546), 0, 32)

# --- Carregando imagens ---
background_filename = './images/bg.png'
frog_filename = './images/sprite_sheets_up.png'
arrived_filename = './images/frog_arrived.png'
car1_filename = './images/car1.png'
car2_filename = './images/car2.png'
car3_filename = './images/car3.png'
car4_filename = './images/car4.png'
car5_filename = './images/car5.png'
plataform_filename = './images/tronco.png'

background = pygame.image.load(background_filename).convert()
sprite_sapo = pygame.image.load(frog_filename).convert_alpha()
sprite_arrived = pygame.image.load(arrived_filename).convert_alpha()
sprite_car1 = pygame.image.load(car1_filename).convert_alpha()
sprite_car2 = pygame.image.load(car2_filename).convert_alpha()
sprite_car3 = pygame.image.load(car3_filename).convert_alpha()
sprite_car4 = pygame.image.load(car4_filename).convert_alpha()
sprite_car5 = pygame.image.load(car5_filename).convert_alpha()
sprite_plataform = pygame.image.load(plataform_filename).convert_alpha()

# --- Carregando Efeitos Sonoros ---
hit_sound = pygame.mixer.Sound('./sounds/boom.wav')
agua_sound = pygame.mixer.Sound('./sounds/agua.wav')
chegou_sound = pygame.mixer.Sound('./sounds/success.wav')
trilha_sound = pygame.mixer.Sound('./sounds/guimo.wav')

pygame.display.set_caption('Frogger')
clock = pygame.time.Clock()



import pygame
from pygame.locals import Rect

class IsInStreet(py_trees.behaviour.Behaviour):
    def __init__(self, frog):
        super().__init__("IsInStreet")
        self.frog = frog

    def update(self):
        if self.frog.position[1] > 241:  # Frog is below the river section
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class IsInRiver(py_trees.behaviour.Behaviour):
    def __init__(self, frog):
        super().__init__("IsInRiver")
        self.frog = frog

    def update(self):
        if 241 >= self.frog.position[1] > 46:  # Frog is in the river section
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class IsInSafeZone(py_trees.behaviour.Behaviour):
    def __init__(self, frog):
        super().__init__("IsInSafeZone")
        self.frog = frog

    def update(self):
        if self.frog.position[1] <= 46:  # Frog is near the top of the screen
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE
       
class HandleSafeZone(py_trees.behaviour.Behaviour):
    def __init__(self, frog, safe_zones):
        super().__init__("HandleSafeZone")
        self.frog = frog
        self.safe_zones = safe_zones


    def update(self):
        
        # Check if there's a safe zone directly in front of the frog
        for zone in self.safe_zones:
            if abs(self.frog.position[0] - zone.x) <= 4:  # Tolerance of ±2 pixels for alignment
                self.frog.moveFrog("up")  # Move into the safe zone if aligned vertically
                return py_trees.common.Status.SUCCESS

        # No safe zone to move into
        return py_trees.common.Status.FAILURE


class HandleRiver(py_trees.behaviour.Behaviour):
    def __init__(self, frog, platforms):
        super().__init__("HandleRiver")
        self.frog = frog
        self.platforms = platforms

    def update(self):

        # Check if there's a platform directly in front of the frog
        platform_in_front = None
        for platform in self.platforms:
            if platform.rect().colliderect(Rect(self.frog.position[0], self.frog.position[1] - 39, 30, 30)):
                platform_in_front = platform
                break

        if platform_in_front:
            # Move up if a platform is directly in front
            self.frog.moveFrog("up")
            return py_trees.common.Status.SUCCESS

        # If the frog is near the edges of the playable area
        if self.frog.position[0] <= 30:  # Near the left edge
            self.frog.moveFrog("right")  # Move right to avoid edge
            return py_trees.common.Status.SUCCESS
        elif self.frog.position[0] >= 390:  # Near the right edge
            self.frog.moveFrog("left")  # Move left to avoid edge
            return py_trees.common.Status.SUCCESS

        # No platform in front and not near edges
        return py_trees.common.Status.FAILURE


class HandleStreet(py_trees.behaviour.Behaviour):
    def __init__(self, frog, enemies):
        super().__init__("HandleStreet")
        self.frog = frog
        self.enemies = enemies

    def update(self):

        # Define the danger zones
        danger_zone_up = Rect(self.frog.position[0] - 15, self.frog.position[1] - 78, 60, 78)
        danger_zone_left = Rect(self.frog.position[0] - 78, self.frog.position[1], 78, 30)
        danger_zone_right = Rect(self.frog.position[0] + 30, self.frog.position[1], 78, 30)

        # Flags for safe directions
        up_safe = True
        left_safe = True
        right_safe = True

        # Check for cars in each danger zone
        for car in self.enemies:
            car_rect = car.rect()

            if danger_zone_up.colliderect(car_rect):
                up_safe = False
            if danger_zone_left.colliderect(car_rect) and car.way == "right":
                left_safe = False
            if danger_zone_right.colliderect(car_rect) and car.way == "left":
                right_safe = False

        # Movement priority: Up > Left > Right
        if up_safe:
            self.frog.moveFrog("up")
            return py_trees.common.Status.SUCCESS
        elif left_safe and self.frog.position[0] > 2:
            self.frog.moveFrog("left")
            return py_trees.common.Status.SUCCESS
        elif right_safe and self.frog.position[0] < 401:
            self.frog.moveFrog("right")
            return py_trees.common.Status.SUCCESS

        # No direction is safe
        return py_trees.common.Status.FAILURE


# Build the Behavior Tree
def build_behavior_tree(frog, enemies, platforms, safe_zones):
    # Create root selector
    root = py_trees.composites.Selector("Root",memory=False)

    # Create condition and action pairs
    street_condition = IsInStreet(frog)
    river_condition = IsInRiver(frog)
    safe_zone_condition = IsInSafeZone(frog)

    handle_street = HandleStreet(frog, enemies)
    handle_river = HandleRiver(frog, platforms)
    handle_safe_zone = HandleSafeZone(frog, safe_zones)

    # Combine conditions and actions into sequences
    street_sequence = py_trees.composites.Sequence("StreetSequence",memory=False)
    street_sequence.add_children([street_condition, handle_street])

    river_sequence = py_trees.composites.Sequence("RiverSequence",memory=False)
    river_sequence.add_children([river_condition, handle_river])

    safe_zone_sequence = py_trees.composites.Sequence("SafeZoneSequence",memory=False)
    safe_zone_sequence.add_children([safe_zone_condition, handle_safe_zone])

    # Add everything to the root
    root.add_children([street_sequence, river_sequence, safe_zone_sequence])

    return root



class Object():
    def __init__(self,position,sprite):
        self.sprite = sprite
        self.position = position

    def draw(self):
        screen.blit(self.sprite,(self.position))

    def rect(self):
        return Rect(self.position[0],self.position[1],self.sprite.get_width(),self.sprite.get_height())


class Frog(Object):


    def __init__(self,position,sprite_sapo):
        self.sprite = sprite_sapo
        self.position = position
        self.lives = 10
        self.animation_counter = 0
        self.animation_tick = 1
        self.way = "UP"
        self.can_move = 1
        self.move_cooldown = 0  # Cooldown timer (ticks until the next move is allowed)

    def updateSprite(self,key_pressed):
        if self.way != key_pressed:
            self.way = key_pressed
            if self.way == "up":
                frog_filename = './images/sprite_sheets_up.png'
                self.sprite = pygame.image.load(frog_filename).convert_alpha()
            elif self.way == "down":
                frog_filename = './images/sprite_sheets_down.png'
                self.sprite = pygame.image.load(frog_filename).convert_alpha()
            elif self.way == "left":
                frog_filename = './images/sprite_sheets_left.png'
                self.sprite = pygame.image.load(frog_filename).convert_alpha()
            elif self.way == "right":
                frog_filename = './images/sprite_sheets_right.png'
                self.sprite = pygame.image.load(frog_filename).convert_alpha()

        
    def moveFrog(self,key_pressed):
        #Tem que fazer o if das bordas da tela ainda
        #O movimento na horizontal ainda não ta certin

        if not self.can_move or self.move_cooldown > 0:
            return  # If cooldown is active, don't move
        
        if self.animation_counter == 0 :
            self.updateSprite(key_pressed)
        self.incAnimationCounter()
        if key_pressed == "up":
            if self.position[1] > 39:
                self.position[1] = self.position[1]-13
        elif key_pressed == "down":
            if self.position[1] < 473:
                self.position[1] = self.position[1]+13
        if key_pressed == "left":
            if self.position[0] > 2:
                if self.animation_counter == 2 :
                    self.position[0] = self.position[0]-13
                else:
                    self.position[0] = self.position[0]-14
        elif key_pressed == "right":
            if self.position[0] < 401:
                if self.animation_counter == 2 :
                    self.position[0] = self.position[0]+13
                else:
                    self.position[0] = self.position[0]+14
                # Reset the cooldown after moving
        self.move_cooldown = 2  # Wait X amount of ticks ticks before the next move


    def animateFrog(self,key_pressed):
        if self.animation_counter != 0 :
            if self.animation_tick <= 0 :
                self.moveFrog(key_pressed)
                self.animation_tick = 1
            else :
                self.animation_tick = self.animation_tick - 1

    def setPos(self,position):
        self.position = position

    def decLives(self):
        self.lives = self.lives - 1

    def cannotMove(self):
        self.can_move = 0

    def incAnimationCounter(self):
        self.animation_counter = self.animation_counter + 1
        if self.animation_counter == 3 :
            self.animation_counter = 0
            self.can_move = 1

    def frogDead(self,game):
        global death_positions  # Use the global death_positions list
        # Add the current position to the death_positions list
        death_positions.append((self.position[0] + 15, self.position[1] + 15))  # Center of the frog
        self.setPositionToInitialPosition()
        self.decLives()
        game.resetTime()
        self.animation_counter = 0
        self.animation_tick = 1
        self.way = "UP"
        self.can_move = 1

    def setPositionToInitialPosition(self):
        self.position = [207, 475]

    def draw(self):
        current_sprite = self.animation_counter * 30
        screen.blit(self.sprite,(self.position),(0 + current_sprite, 0, 30, 30 + current_sprite))

    def rect(self):
        return Rect(self.position[0],self.position[1],30,30)

class Enemy(Object):
    def __init__(self,position,sprite_enemy,way,factor):
        self.sprite = sprite_enemy
        self.position = position
        self.way = way
        self.factor = factor

    def move(self,speed):
        if self.way == "right":
            self.position[0] = self.position[0] + speed * self.factor
        elif self.way == "left":
            self.position[0] = self.position[0] - speed * self.factor


class Plataform(Object):
    def __init__(self,position,sprite_plataform,way):
        self.sprite = sprite_plataform
        self.position = position
        self.way = way

    def move(self,speed):
        if self.way == "right":
            self.position[0] = self.position[0] + speed
        elif self.way == "left":
            self.position[0] = self.position[0] - speed


class Game():
    def __init__(self,speed,level):
        self.speed = speed
        self.level = level
        self.points = 0
        self.time = 30
        self.gameInit = 0

    def incLevel(self):
        self.level = self.level + 1

    def incSpeed(self):
        self.speed = self.speed + 1

    def incPoints(self,points):
        self.points = self.points + points

    def decTime(self):
        self.time = self.time - 1

    def resetTime(self):
        self.time = 30


#Funções gerais
def drawList(list):
    for i in list:
        i.draw()

def moveList(list,speed):
    for i in list:
        i.move(speed)

def destroyEnemys(list):
    for i in list:
        if i.position[0] < -80:
            list.remove(i)
        elif i.position[0] > 516:
            list.remove(i)

def destroyPlataforms(list):
    for i in list:
        if i.position[0] < -100:
            list.remove(i)
        elif i.position[0] > 448:
            list.remove(i)

def createEnemys(list,enemys,game):
    for i, tick in enumerate(list):
        list[i] = list[i] - 1
        if tick <= 0:
            if i == 0:
                list[0] = (40*game.speed)/game.level
                position_init = [-55,436]
                enemy = Enemy(position_init,sprite_car1,"right",1)
                enemys.append(enemy)
            elif i == 1:
                list[1] = (30*game.speed)/game.level
                position_init = [506, 397]
                enemy = Enemy(position_init,sprite_car2,"left",2)
                enemys.append(enemy)
            elif i == 2:
                list[2] = (40*game.speed)/game.level
                position_init = [-80, 357]
                enemy = Enemy(position_init,sprite_car3,"right",2)
                enemys.append(enemy)
            elif i == 3:
                list[3] = (30*game.speed)/game.level
                position_init = [516, 318]
                enemy = Enemy(position_init,sprite_car4,"left",1)
                enemys.append(enemy)
            elif i == 4:
                list[4] = (50*game.speed)/game.level
                position_init = [-56, 280]
                enemy = Enemy(position_init,sprite_car5,"right",1)
                enemys.append(enemy)

def createPlataform(list,plataforms,game):
    for i, tick in enumerate(list):
        list[i] = list[i] - 1
        if tick <= 0:
            if i == 0:
                list[0] = (30*game.speed)/game.level
                position_init = [-100,200]
                plataform = Plataform(position_init,sprite_plataform,"right")
                plataforms.append(plataform)
            elif i == 1:
                list[1] = (30*game.speed)/game.level
                position_init = [448, 161]
                plataform = Plataform(position_init,sprite_plataform,"left")
                plataforms.append(plataform)
            elif i == 2:
                list[2] = (40*game.speed)/game.level
                position_init = [-100, 122]
                plataform = Plataform(position_init,sprite_plataform,"right")
                plataforms.append(plataform)
            elif i == 3:
                list[3] = (40*game.speed)/game.level
                position_init = [448, 83]
                plataform = Plataform(position_init,sprite_plataform,"left")
                plataforms.append(plataform)
            elif i == 4:
                list[4] = (20*game.speed)/game.level
                position_init = [-100, 44]
                plataform = Plataform(position_init,sprite_plataform,"right")
                plataforms.append(plataform)

def carChangeRoad(enemys):
    enemy = Random.choice(enemys)
    initialPosition = enemy.position[1]

    choice = Random.randint(1,2)
    if (choice % 2 == 0):
        enemy.position[1] = enemy.position[1] + 39
    else :
        enemy.position[1] = enemy.position[1] - 39

    if enemy.position[1] > 436:
        enemy.position[1] = initialPosition
    elif enemy.position[1] < 280:
        enemy.position[1] = initialPosition


def frogOnTheStreet(frog,enemys,game):
    for i in enemys:
        enemyRect = i.rect()
        frogRect = frog.rect()
        if frogRect.colliderect(enemyRect):
            hit_sound.play()
            frog.frogDead(game)

def frogInTheLake(frog,plataforms,game):
    #se o sapo esta sob alguma plataforma Seguro = 1
    seguro = 0
    wayPlataform = ""
    for i in plataforms:
        plataformRect = i.rect()
        frogRect = frog.rect()
        if frogRect.colliderect(plataformRect):
            seguro = 1
            wayPlataform = i.way

    if seguro == 0:
        agua_sound.play()
        frog.frogDead(game)

    elif seguro == 1:
        if wayPlataform == "right":
            frog.position[0] = frog.position[0] + game.speed

        elif wayPlataform == "left":
            frog.position[0] = frog.position[0] - game.speed

def frogArrived(frog,chegaram,game):
    if frog.position[0] > 33 and frog.position[0] < 53:
        position_init = [43,7]
        createArrived(frog,chegaram,game,position_init)

    elif frog.position[0] > 115 and frog.position[0] < 135:
        position_init = [125,7]
        createArrived(frog,chegaram,game,position_init)

    elif frog.position[0] > 197 and frog.position[0] < 217:
        position_init = [207,7]
        createArrived(frog,chegaram,game,position_init)

    elif frog.position[0] > 279 and frog.position[0] < 299:
        position_init = [289,7]
        createArrived(frog,chegaram,game,position_init)

    elif frog.position[0] > 361 and frog.position[0] < 381:
        position_init = [371,7]
        createArrived(frog,chegaram,game,position_init)

    else:
        frog.position[1] = 46
        frog.animation_counter = 0
        frog.animation_tick = 1
        frog.can_move = 1


def whereIsTheFrog(frog):
    #Se o sapo ainda não passou da estrada
    if frog.position[1] > 240 :
        frogOnTheStreet(frog,enemys,game)

    #Se o sapo chegou no rio
    elif frog.position[1] < 240 and frog.position[1] > 40:
        frogInTheLake(frog,plataforms,game)

    #sapo chegou no objetivo
    elif frog.position[1] < 40 :
        frogArrived(frog,chegaram,game)


def createArrived(frog,chegaram,game,position_init):
    sapo_chegou = Object(position_init,sprite_arrived)
    chegaram.append(sapo_chegou)

        # Remove the safe zone that the frog entered from the SAFE_ZONES list
    for zone in SAFE_ZONES:
        if zone.collidepoint(position_init):
            SAFE_ZONES.remove(zone)
            break  # Exit the loop once the safe zone is removed

    chegou_sound.play()
    frog.setPositionToInitialPosition()
    game.incPoints(10 + game.time)
    game.resetTime()
    frog.animation_counter = 0
    frog.animation_tick = 1
    frog.can_move = 1


def nextLevel(chegaram,enemys,plataforms,frog,game):
    if len(chegaram) == 5:
        chegaram[:] = []
        frog.setPositionToInitialPosition()
        game.incLevel()
        game.incSpeed()
        game.incPoints(100)
        game.resetTime()

def resetSafeZones():
    global SAFE_ZONES
    SAFE_ZONES = [
        Rect(33, 7, 20, 20),
        Rect(115, 7, 20, 20),
        Rect(197, 7, 20, 20),
        Rect(279, 7, 20, 20),
        Rect(361, 7, 20, 20),
    ]

#trilha_sound.play(-1)
text_info = menu_font.render(('Press any button to start!'),1,(0,0,0))
gameInit = 0

SAFE_ZONES = [
    Rect(33, 7, 20, 20),
    Rect(115, 7, 20, 20),
    Rect(197, 7, 20, 20),
    Rect(279, 7, 20, 20),
    Rect(361, 7, 20, 20),
]

death_positions = []  # List to store the positions where the frog dies

while gameInit == 0:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == KEYDOWN:
            gameInit = 1

    screen.blit(background, (0, 0))
    screen.blit(text_info,(80,150))
    pygame.display.update()

while True:
    gameInit = 1
    game = Game(3,1)
    #Change initial Frog position to test different behaviours
    #475 to test street, 240 to test river
    frog_initial_position = [207,475]
    frog = Frog(frog_initial_position,sprite_sapo)

    enemys = []
    plataforms = []
    chegaram = []
    #30 ticks == 1 segundo
    #ticks_enemys = [120, 90, 120, 90, 150]
    #ticks_plataforms = [90, 90, 120, 120, 60]
    ticks_enemys = [30, 0, 30, 0, 60]
    ticks_plataforms = [0, 0, 30, 30, 30]
    ticks_time = 30
    pressed_keys = 0
    key_pressed = 0

    # Inside the main game loop
    behavior_tree = build_behavior_tree(frog, enemys, plataforms, SAFE_ZONES)

    while frog.lives > 0:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
        if not ticks_time:
            ticks_time = 30
            game.decTime()
        else:
            ticks_time -= 1

        if game.time == 0:
            frog.frogDead(game)

        if frog.move_cooldown > 0:
            frog.move_cooldown -= 1

        createEnemys(ticks_enemys,enemys,game)
        createPlataform(ticks_plataforms,plataforms,game)

        moveList(enemys,game.speed)
        moveList(plataforms,game.speed)

        whereIsTheFrog(frog)

        nextLevel(chegaram,enemys,plataforms,frog,game)

        text_info1 = info_font.render(('Level: {0}               Points: {1}'.format(game.level,game.points)),1,(255,255,255))
        text_info2 = info_font.render(('Time: {0}           Lifes: {1}'.format(game.time,frog.lives)),1,(255,255,255))
        screen.blit(background, (0, 0))
        screen.blit(text_info1,(10,520))
        screen.blit(text_info2,(250,520))

        random = Random.randint(0,100)
        if(random % 100 == 0):
            carChangeRoad(enemys)

        drawList(enemys)
        drawList(plataforms)
        drawList(chegaram)

        delay = Random.randint(3,5)

        #Adding some delay to start the frog at a random time
        if game.time <= 30 - delay:
            behavior_tree.tick_once()

        frog.draw()

        for pos in death_positions:
            pygame.draw.line(screen, (255, 0, 0), (pos[0] - 10, pos[1] - 10), (pos[0] + 10, pos[1] + 10), 2)  # Diagonal line 1
            pygame.draw.line(screen, (255, 0, 0), (pos[0] - 10, pos[1] + 10), (pos[0] + 10, pos[1] - 10), 2)  # Diagonal line 2


        destroyEnemys(enemys)
        destroyPlataforms(plataforms)

        pygame.display.update()
        time_passed = clock.tick(30)

    while gameInit == 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                gameInit = 0

        #Change the Spanish to english
        screen.blit(background, (0, 0))
        text = game_font.render('GAME OVER', 1, (255, 0, 0))
        text_points = game_font.render(('Points: {0}'.format(game.points)),1,(255,0,0))
        text_reiniciar = info_font.render('Press Any Key to Restart!',1,(255,0,0))
        screen.blit(text, (75, 120))
        screen.blit(text_points,(10,170))
        screen.blit(text_reiniciar,(70,250))
        resetSafeZones()
        death_positions.clear()  # Clear the death positions
        pygame.display.update()
