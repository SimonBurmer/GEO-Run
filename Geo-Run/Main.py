import pygame
from obstacle import Obstacle
from player import Player
from ground import Ground
from settings import *
import os
import time 
from button import Button
pygame.font.init()

#Game class represents the game 
class Game:
    def __init__(self):
        #initialize game window, etc
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dino-Run")
        self.clock = pygame.time.Clock()
        #for programm loop
        self.running = True
        #for game loop
        self.playing = True
        #gamespeed (FPS)
        self.speed = 60
        #determines is a bossobstacle is in the game
        self.soon_boss_Obstacle = False
        #for jumping into if-statement only once
        self.once = True

        self.load_data()

    def load_data(self):
        self.local_dir = os.path.dirname(__file__)

        #sounds
        self.sound_Jump = pygame.mixer.Sound(self.local_dir +'/sounds/Jumpsound.wav')
        self.sound_Die = pygame.mixer.Sound(self.local_dir +'/sounds/diesound.wav')
        self.sound_Die.set_volume(0.1)

        #load high score
        with open(self.local_dir + "/highscore.txt", 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0


    def new(self):
        #starts a new game
        self.score = 0
        #gamesound in infinity loop
        pygame.mixer.music.load(self.local_dir +'/sounds/Backgroundmusic.wav')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

        #creating the game objects 
        self.all_sprites = pygame.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)

        self.ground = Ground(*GROUND)
        self.all_sprites.add(self.ground)

        self.obstacles = [Obstacle()]
        
        self.run()

    def run(self):
        #Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(self.speed)
            self.events()
            self.update()
            self.draw()

    def update(self):
        #Game Loop - Update
        #update all_sprite group
        self.all_sprites.update()
        #update the obstacles
        for obs in self.obstacles:
            obs.update()

        #check if player hits a ground - only if falling
        if self.player.velocity.y > 0:
            hits = pygame.sprite.collide_rect(self.player, self.ground)
            #if player hits a Ground, put him on the ground
            if hits:
                self.player.pos.y = self.ground.rect.y
                self.player.velocity.y = 0
        
        #ckeck if player hits a obstacle 
        for obs in self.obstacles:
            if obs.rect.left < PLAYER_X + 30:
                hits = pygame.sprite.collide_rect(self.player, obs)
                if hits:
                    self.playing = False

        #kill old obstacles and count up score 
        for i, obs in enumerate(self.obstacles):
            if obs.rect.left < -60:
                self.score += 10
                self.obstacles.pop(i)                

        #only spawn new obstacles if the last one is far enough away
        if not self.soon_boss_Obstacle and self.obstacles[-1].rect.x < 830:
            self.obstacles.append(Obstacle())

        #boss is comming
        if (self.score+10) % 90 == 0:
                self.soon_boss_Obstacle = True
                self.t0 = time.perf_counter()
                self.once = False

        #timer for boss spawntime
        self.t1 = time.perf_counter()
        
        #check if t0 existist
        try:
            self.t0
        except AttributeError:
            var_exists = False
        else:
            var_exists = True
        #spawns the boss
        if var_exists:
            if self.t1-self.t0 > 3 and not self.once:
                self.soon_boss_Obstacle = False
                self.once = True
                bossObs = Obstacle()
                bossObs.speed = 30  
                bossObs.setcolor(RED)
                self.obstacles.append(bossObs)
    
    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # check for jumping inquiry
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                    self.sound_Jump.play()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BLACK)

        self.all_sprites.draw(self.screen)

        for obs in self.obstacles:
            obs.draw(self.screen)

        self.draw_text("Score: "+str(self.score), 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("High Score: " + str(self.highscore), 28, WHITE, WIDTH / 2, HEIGHT / 4 + 35)
        
        # *after* drawing everything, flip the display
        pygame.display.flip()

    def show_start_screen(self):
        #startsound
        pygame.mixer.music.load(self.local_dir +'/sounds/Startsound.wav')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(1)
        
        # game start screen
        self.screen.fill(BLACK)

        #Menubuttons
        self.all_buttons = pygame.sprite.Group()
        self.start_button = Button(WIDTH/2-100,HEIGHT/2.5,200,40,runGame,30,"Start")
        self.exit_button = Button(WIDTH/2-100,HEIGHT/2,200,40,exit,30,"Exit")
        self.Settings_button = Button(WIDTH/2-100,HEIGHT/1.7,200,40,exit,30,"Settings")
        self.all_buttons.add(self.start_button,self.exit_button,self.Settings_button) 
        self.all_buttons.draw(self.screen)

        #Heading 
        self.draw_text("GEO-RUN", 48, WHITE, WIDTH / 2, HEIGHT / 4)

        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False

                for button in self.all_buttons:
                    button.handle_event(event)
                    self.all_buttons.draw(self.screen)
                    pygame.display.flip()


    def show_die_screen(self):
        #gameover/continue
        self.sound_Die.play()
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)

        #highscore 
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 30, WHITE, WIDTH / 2, HEIGHT / 4 + 40)
            self.draw_text(str(self.highscore), 30, WHITE, WIDTH / 2, HEIGHT / 4 + 65)
            with open(self.local_dir + "/highscore.txt", 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("Your Score: " + str(self.score), 30, WHITE, WIDTH / 2, HEIGHT / 4 + 60)
            self.draw_text("High Score: " + str(self.highscore), 30, WHITE, WIDTH / 2, HEIGHT / 4 + 40)

        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                    pygame.quit()
                if event.type == pygame.KEYUP:
                    waiting = False

    #for easy text creating 
    def draw_text(self, text, size, color, x, y):
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


#main game loop 
def runGame():
    while g.running:
        g.new()
        if not g.running:
            pygame.quit()
        g.show_die_screen()


def exit():
    pygame.quit()

g = Game()
g.show_start_screen()
pygame.quit()



