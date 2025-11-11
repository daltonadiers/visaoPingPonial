from collections import deque
from dataclasses import dataclass
import math


WRIST=0
THUMB_TIP,THUMB_IP=4,3
INDEX_TIP,INDEX_PIP=8,6
MIDDLE_TIP,MIDDLE_PIP=12,10
RING_TIP,RING_PIP=16,14
PINKY_TIP,PINKY_PIP=20,18


ARM_UP_Y_THR = 0.40

@dataclass
class HandState:
    handedness: str         
    x: float; y: float      
    fingers_up: tuple       
    is_thumbs_up: bool
    is_thumbs_down: bool
    one_finger: bool
    two_fingers: bool
    v_inverted: bool
    is_open_palm: bool      
    is_arm_up: bool         

def _finger_up(lm, tip, pip, axis='y'):
    if axis=='y':
        return lm[tip].y < lm[pip].y
    return lm[tip].x < lm[pip].x

def _thumb_up(lm, handed):
    
    
    tip = lm[THUMB_TIP].x; ip = lm[THUMB_IP].x
    return (tip > ip) if handed=='Right' else (tip < ip)

def _thumb_down(lm, handed):
    tip = lm[THUMB_TIP].x; ip = lm[THUMB_IP].x
    return (tip < ip) if handed=='Right' else (tip > ip)

def classify_hand(hand_landmarks, handedness:str)->HandState:
    lm = hand_landmarks.landmark
    f_index = _finger_up(lm, INDEX_TIP, INDEX_PIP)
    f_middle= _finger_up(lm, MIDDLE_TIP, MIDDLE_PIP)
    f_ring  = _finger_up(lm, RING_TIP, RING_PIP)
    f_pinky = _finger_up(lm, PINKY_TIP, PINKY_PIP)
    
    
    f_thumb = _thumb_up(lm, handedness) or _thumb_down(lm, handedness)

    one = (f_index and not f_middle and not f_ring and not f_pinky)
    two = (f_index and f_middle and not f_ring and not f_pinky)

    v_inv = two and (lm[INDEX_TIP].x - lm[MIDDLE_TIP].x)**2 + (lm[INDEX_TIP].y - lm[MIDDLE_TIP].y)**2 < 0.0025

    open_palm = f_thumb and f_index and f_middle and f_ring and f_pinky
    arm_up = lm[WRIST].y < ARM_UP_Y_THR

    return HandState(
        handedness=handedness,
        x=lm[WRIST].x, y=lm[WRIST].y,
        fingers_up=(f_thumb, f_index, f_middle, f_ring, f_pinky),
        is_thumbs_up=_thumb_up(lm, handedness),
        is_thumbs_down=_thumb_down(lm, handedness),
        one_finger=one, two_fingers=two, v_inverted=v_inv,
        is_open_palm=open_palm,
        is_arm_up=arm_up
    )

@dataclass
class Gesture:
    kind: str 

def detect_gestures(hands: list[HandState])->dict[str,list[Gesture]]:
    out = {'L':[], 'R':[]}
    for h in hands:
        side = 'L' if h.handedness=='Left' else 'R'
        if h.is_thumbs_up:
            out[side].append(Gesture('REQUEST'))
        if h.is_open_palm:
            out[side].append(Gesture('CONFIRM'))
    return out
