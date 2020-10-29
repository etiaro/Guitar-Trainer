import random
import musicalbeeps

from listenNote import waitToPlay, end

player = musicalbeeps.Player(volume = 1, mute_output=True)
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

import threading
import pygame
import time
  
pygame.init() 
X = 400
Y = 400
display_surface = pygame.display.set_mode((X, Y )) 
pygame.display.set_caption('Show Text') 
font = pygame.font.Font('freesansbold.ttf', 70) 


note = random.choice(notes)
player.play_note(note, 0.2)
th = threading.Thread(target=waitToPlay, args=({note},))
th.start()

first_done = 0
prev_time = time.time()
target_fps = 60

while True :
    if not th.is_alive():
        old = note
        while note is old:
            note = random.choice(notes)
        player.play_note(note, 0.2)
        th = threading.Thread(target=waitToPlay, args=({note},))
        th.start()
        first_done=1
    

    text = font.render(note, True, (255,255,255)) 
    textRect = text.get_rect()  
    textRect.center = (X // 2, Y // 2) 

    display_surface.fill((0,0,0)) 
    
    if first_done > 0:
        display_surface.fill((0,255,0)) 
        first_done = (first_done + 1) % 60


    display_surface.blit(text, textRect) 
    for event in pygame.event.get() : 
        if event.type == pygame.QUIT : 
            pygame.quit() 
            end()
            quit()  


    curr_time = time.time()#so now we have time after processing
    diff = curr_time - prev_time#frame took this much time to process and render
    delay = max(1.0/target_fps - diff, 0)#if we finished early, wait the remaining time to desired fps, else wait 0 ms!
    time.sleep(delay)
    fps = 1.0/(delay + diff)#fps is based on total time ("processing" diff time + "wasted" delay time)
    prev_time = curr_time
    pygame.display.set_caption("{0}: {1:.2f}".format("NOTE TRAINER", fps))

    pygame.display.update()

