import random
import musicalbeeps

from listenNote import soundAnalyzer

#player = musicalbeeps.Player(volume = 1, mute_output=True)
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
chords = [' Major', 'M']

def unfreeze(recInput):
    recInput['freeze'] = False

def getChordNotes(rootNote, chordType):
    if chordType == ' Major':
        rootInd = notes.index(rootNote)
        return {rootNote, notes[(rootInd+4)%len(notes)], notes[(rootInd+7)%len(notes)]}
    if chordType == 'M':
        rootInd = notes.index(rootNote)
        return {rootNote, notes[(rootInd+3)%len(notes)], notes[(rootInd+7)%len(notes)]}

def getChordLen(chordType):
    return len(getChordNotes('C', chordType))

import threading
import pygame
import time
  
pygame.init() 
X = 400
Y = 400
display_surface = pygame.display.set_mode((X, Y)) 
pygame.display.set_caption('NOTE TRAINER') 
font = pygame.font.Font('freesansbold.ttf', 70) 

rootNote = random.choice(notes)
chordType = random.choice(chords)
recOutput = {"volume": 0, 'fired': [], 'repeated': 0}
recInput = {'rate': 48000, 'chunk': 2**12, 'chunk_num': 16, 'kill': False, 'freeze': False,
            'notesNum': getChordLen(chordType), 'threshold': 0.2, 'callsToFire': 20, 
            'acceptableSkip': 15, 'acceptableError': 5}
#player.play_note(note, 0.2)

th = threading.Thread(target=soundAnalyzer, args=(recInput, recOutput))
th.start()

good_frame = 0
sound_frame = 0
bad_frame = 0
old_note = rootNote
old_type = chordType
prev_time = time.time()
target_fps = 60

while True :
    if len(recOutput['fired']) > 0:
        if recOutput['fired'][0] == getChordNotes(rootNote, chordType):
            recInput['freeze'] = True
            old_note = rootNote
            old_type = chordType
            while rootNote is old_note and chordType is old_type: 
                rootNote = random.choice(notes)
                chordType = random.choice(chords)
            good_frame = 1
            bad_frame = 0
        else:
            bad_frame = 1
        tmp = recOutput['fired'][0]
        while len(recOutput['fired']) > 0 and recOutput['fired'][0] == tmp:
            recOutput['fired'].pop(0)

    

    
    display_surface.fill((0,0,0))
    text = font.render(rootNote + chordType, True, (255,255,255))
    
    if bad_frame > 0:
        display_surface.fill((255,0,0)) 
        pygame.draw.rect(display_surface,(100,0,0),(0,50,X,10))         #acceptance bar
        bad_frame = (bad_frame + 1) % 60

    if good_frame > 0:
        text = font.render(old_note + old_type, True, (255,255,255))
        display_surface.fill((0,255,0)) 
        pygame.draw.rect(display_surface,(0,100,0),(0,50,X,10))         #acceptance bar
        good_frame = (good_frame + 1) % 60
        if good_frame == 0:
            #player.play_note(note, 0.2)
            recInput['notesNum'] = getChordLen(chordType)
            threading.Timer(0.5, unfreeze, (recInput, )).start()
    
    pygame.draw.rect(display_surface,(255,255,0),(0,50,X*recOutput['repeated']/recInput['callsToFire'],10))         #acceptance bar
    pygame.draw.rect(display_surface,(255,255,255),(0,0,X,50))
    pygame.draw.rect(display_surface,(100,100,100),(0,0,X*recOutput["volume"],50))
    pygame.draw.rect(display_surface,(0,0,0),(X*recInput['threshold'],0,2,50))

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

