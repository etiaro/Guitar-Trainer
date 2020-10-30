import random
import musicalbeeps

from listenNote import soundAnalyzer

player = musicalbeeps.Player(volume = 1, mute_output=True)
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
def unfreeze(recInput):
    recInput['freeze'] = False

import threading
import pygame
import time
  
pygame.init() 
X = 400
Y = 400
display_surface = pygame.display.set_mode((X, Y)) 
pygame.display.set_caption('NOTE TRAINER') 
font = pygame.font.Font('freesansbold.ttf', 70) 

note = random.choice(notes)
recOutput = {"volume": 0, 'fired': [], 'repeated': 0}
recInput = {'rate': 48000, 'chunk': 2**10, 'chunk_num': 32, 'kill': False, 'freeze': False,
            'notesNum': 1, 'threshold': 0.2, 'callsToFire': 20, 
            'acceptableSkip': 0, 'acceptableError': 3}
player.play_note(note, 0.2)

th = threading.Thread(target=soundAnalyzer, args=(recInput, recOutput))
th.start()

good_frame = 0
sound_frame = 0
bad_frame = 0
old_note = note
prev_time = time.time()
target_fps = 60

while True :
    if len(recOutput['fired']) > 0:
        if recOutput['fired'][0] == {note}:
            recInput['freeze'] = True
            old_note = note
            while note is old_note:
                note = random.choice(notes)
            good_frame = 1
            bad_frame = 0
        else:
            bad_frame = 1
        tmp = recOutput['fired'][0]
        while len(recOutput['fired']) > 0 and recOutput['fired'][0] == tmp:
            recOutput['fired'].pop(0)

    

    display_surface.fill((0,0,0)) 
    text = font.render(note, True, (255,255,255))


    if bad_frame > 0:
        display_surface.fill((255,0,0)) 
        pygame.draw.rect(display_surface,(100,0,0),(0,50,X,10))         #acceptance bar
        bad_frame = (bad_frame + 1) % 60

    if good_frame > 0:
        text = font.render(old_note, True, (255,255,255))
        display_surface.fill((0,255,0)) 
        pygame.draw.rect(display_surface,(0,100,0),(0,50,X,10))         #acceptance bar
        good_frame = (good_frame + 1) % 60
        if good_frame == 0:
            player.play_note(note, 0.2)
            threading.Timer(0.5, unfreeze, (recInput, )).start()
            
    
    pygame.draw.rect(display_surface,(255,255,0),(0,50,X*recOutput['repeated']/recInput['callsToFire'],10))         #acceptance bar
    pygame.draw.rect(display_surface,(255,255,255),(0,0,X,50))      #volume bar
    pygame.draw.rect(display_surface,(100,100,100),(0,0,X*recOutput["volume"],50))      #volume value
    pygame.draw.rect(display_surface,(0,0,0),(X*recInput['threshold'],0,2,50))              #volume threshold

    textRect = text.get_rect()  
    textRect.center = (X // 2, Y // 2) 
    display_surface.blit(text, textRect) 

    for event in pygame.event.get() : 
        if event.type == pygame.QUIT : 
            pygame.quit() 
            recInput['kill'] = True
            th.join()
            quit()

    if pygame.mouse.get_pressed()[0]:
        pos = pygame.mouse.get_pos()
        if pos[1] <= 50: #it's volume bar
            recInput['threshold'] = pos[0] / X


    curr_time = time.time()#so now we have time after processing
    diff = curr_time - prev_time#frame took this much time to process and render
    delay = max(1.0/target_fps - diff, 0)#if we finished early, wait the remaining time to desired fps, else wait 0 ms!
    time.sleep(delay)
    prev_time = curr_time

    pygame.display.update()

