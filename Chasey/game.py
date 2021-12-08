import pygame
from pygame import mixer
import random
import pickle
import neat
import os
import math
import sys

from pygame.sprite import spritecollide

pygame.init()

#distance function
def distance(rectA,rectB):
    return(((rectA.x-rectB.x)**2)+((rectA.y-rectB.y)**2))**0.5
#other distance function
def centDist(rectA):
    return(((rectA.x-res[0]/2)**2)+((rectA.y-res[1]/2)**2))**0.5


#randomizer for movements
def randBool():
    return random.choice([True, False])

#score
s=0
def score():
    global s
    s+=1
    #text for points 
    points=FONT.render("{}".format(s),False,(0,0,0))
    return s

#make the grid
res=(800,600)
screen=pygame.display.set_mode(res)
pygame.display.set_caption('Chasey')
clock=pygame.time.Clock()

#enemy image
BROWN=pygame.image.load("Chasey/Characters/8bitBrownie.png").convert_alpha()
BROWN=pygame.transform.scale(BROWN,(50,50))

#sounds
mixer.init()
mixer.music.load("Chasey/objects/brownieBark.mp3")
mixer.music.set_volume(0.5)

#text
FONT=pygame.font.Font("Chasey/Fonts/arial.ttf",50)

#images
pics=['Chasey/Characters/8bitBrownie.png','Chasey/Characters/8bitNirmR.png']
text_surface=FONT.render("Catch the dog",False,'Black')
winSurface=FONT.render("You Win!!",False,'Black')

#background
grass=pygame.image.load('Chasey/objects/background.jpg')
grass=pygame.transform.scale(grass,res)

#main character
Nirm=pygame.image.load(pics[1]).convert_alpha()
Nirm=pygame.transform.scale(Nirm,(50,100))
NirmX=400
NirmY=400
NirmRect=Nirm.get_rect(topleft=(NirmX,NirmY))
#NirmRect.inflate_ip(-20,-10)
Nspeed=2
facing=True
 
speed=3
#enemy sprite class
class enemy(pygame.sprite.Sprite):
    def __init__(self,posX,posY,up,right):
        super().__init__()
        self.image=BROWN
        self.rect=self.image.get_rect(center=(posX,posY))
        self.up=up
        self.right=right
    def move(self):
        if(self.up):
            self.rect.y-=speed
        else:
            self.rect.y+=speed
        if(self.right):
            self.rect.x+=speed
        else:
            self.rect.x-=speed
    #boundry check
        if self.rect.right>=res[0]:
            self.rect.right=res[0]
        if self.rect.left<=0:
            self.rect.left=0
        if self.rect.top<=0:
            self.rect.top=0
        if self.rect.bottom>=res[1]:
           self.rect.bottom=res[1]

#remove functions
def remove(ind):
    bosses.pop(ind)
    ge.pop(ind)
    nets.pop(ind)
    






#controlling the boss with AI
def eval_genomes(genomes,config):
    global NirmRect,Nirm,bosses,ge,nets, facing, Nspeed
    bosses= []
    ge = []
    nets = []

    for iter, genome in genomes:
        bosses.append(enemy(200,200,True,False))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome,config)
        nets.append(net)
        genome.fitness=0
    



    #actual game loop
    again=True
    while again:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                exit()

        #move the dog
        for dog in bosses:
            dog.move()

        #move player based on keyboard
        # save keyboard inputs for neat
        pressed=[0,0,0,0]
        keys=pygame.key.get_pressed()
        if(keys[pygame.K_w] or keys[pygame.K_UP]):
            NirmRect.y-=Nspeed
            pressed[0]=1
        if(keys[pygame.K_a] or keys[pygame.K_LEFT]):
            if facing:
                Nirm=pygame.transform.flip(Nirm,True,False)
                facing=False
            NirmRect.x-=Nspeed
            pressed[1]=1
        if(keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            if not facing:
                Nirm=pygame.transform.flip(Nirm,True,False)
                facing=True
            NirmRect.x+=Nspeed
            pressed[2]=1
        if(keys[pygame.K_s] or keys[pygame.K_DOWN]):
            NirmRect.y+=Nspeed
            pressed[3]=1
        if(keys[pygame.K_SPACE]):
            Nspeed=11
        else:
            Nspeed=2

        #keeping player in bounds
        if(NirmRect.bottom>=res[1]):
            NirmRect.bottom=res[1]
        elif(NirmRect.top<=0):
            NirmRect.top=0
        if(NirmRect.right>=res[0]):
            NirmRect.right=res[0]
        elif(NirmRect.left<=0):
            NirmRect.left=0

        #output: up left down right
        for i, boss in enumerate(bosses):
            data=[boss.rect.x,NirmRect.x,boss.rect.y,NirmRect.y,
            distance(boss.rect,NirmRect),
            boss.rect.x-NirmRect.x,boss.rect.y-NirmRect.y,
            NirmRect.x-boss.rect.x,NirmRect.y-boss.rect.y,
            pressed[0],pressed[1],pressed[2],pressed[3]
            ]

            output=nets[i].activate(data)
            val=output[0]

            if val>=-1 and val<=-0.5:
                boss.up=True
            if val>=-0.5 and val<=0:
                boss.up=False
            if val>0 and val<=0.5:
                boss.right=True
            if val>=0.5 and val<=0.5:
                boss.right=False
        
        #collisions
        for i, boss in enumerate(bosses):
            #being closer to center is good and player being close to center is good
            #somehow player being in center needs to be optimized
            if(centDist(boss.rect)<100):
                ge[i].fitness+=50
            elif centDist(boss.rect)>100 and centDist(boss.rect)<300:
                ge[i].fitness+=10
            else:
                ge[i].fitness-=5

            ge[i].fitness+=(1/centDist(NirmRect))
            #reward being far from my distance
            if(distance(boss.rect,NirmRect)>200):
                ge[i].fitness+=distance(boss.rect,NirmRect)/70
            else:
                ge[i].fitness-=.1

            #punish corner campers
            count=10
            if(boss.rect.top<=0):
                ge[i].fitness-=3*count
                count+=1
            else:
                ge[i].fitness+=1
            if(boss.rect.bottom>=res[1]):
                ge[i].fitness-=3*count
                count+=1
            else:
                ge[i].fitness+=1
            if(boss.rect.right>=res[0]):
                ge[i].fitness-=3*count
                count+=1
            else:
                ge[i].fitness+=1
            if(boss.rect.left<=0):
                ge[i].fitness-=3*count
            else:
                ge[i].fitness+=1
                

            if(NirmRect.colliderect(boss.rect)):
                #decrease fitness level of brownies that collide
                ge[i].fitness-=15
                remove(i)
            else:
                ge[i].fitness+=1
    
        if len(bosses)==0:
            break

        #place objects
        screen.blit(grass,(0,0))
        for boss in bosses:
            screen.blit(boss.image,boss.rect)
        screen.blit(Nirm,NirmRect) 
        pygame.display.update()
        clock.tick(60) 
   
 
#setup the NEAT
def run(config_path):
    global pop , goodGenes
    configuration=neat.config.Config(
    neat.DefaultGenome,
    neat.DefaultReproduction,
    neat.DefaultSpeciesSet,
    neat.DefaultStagnation,
    config_path)

    pop= neat.Population(configuration)
    #load the good genome
    with open("Chasey\winner.pkl","rb") as f:
        goodGenes=pickle.load(f)
        genomes=[(1,goodGenes)]

    best= pop.run(eval_genomes,100)
    #run for 100 generations
    
    #save the best genome
    with open("testGame\winner.pkl","wb") as f:
        pickle.dump(best,f)
        f.close()

if __name__=='__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config-feedforward.txt")
    run(config_path)