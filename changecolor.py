#!/usr/bin/env python

import time
import piface.pfio
import sys

piface.pfio.init(False)

red = piface.pfio.LED(0)
green = piface.pfio.LED(1)
yellow = piface.pfio.LED(2)
purple = piface.pfio.LED(3)

def all_off():
  red.turn_off()
  green.turn_off()
  yellow.turn_off()
  purple.turn_off()

if (len(sys.argv) == 2):

  if (sys.argv[1] == 'red'):
    red.turn_on()
    purple.turn_off()
    green.turn_off()
 
  if (sys.argv[1] == 'green'):
    red.turn_off()
    purple.turn_off()
    green.turn_on()
		

  if (sys.argv[1] == 'purple'):
    #red.turn_off()
    #green.turn_off()
    yellow.turn_off()
    purple.turn_on()
 
  if (sys.argv[1] == 'init'):
    piface.pfio.init()
    green.turn_on()
    time.sleep(1)
    red.turn_on()
    time.sleep(1)
    yellow.turn_on()
    time.sleep(1)
    purple.turn_on()
    time.sleep(1)
    all_off()

  if (sys.argv[1] == 'off'):
    all_off()

if (len(sys.argv) == 3):

  if (sys.argv[2] == 'on'):

    if (sys.argv[1] == 'red'):
      red.turn_on()

    if (sys.argv[1] == 'green'):
      green.turn_on()

    if (sys.argv[1] == 'purple'):
      purple.turn_on()
 
    if (sys.argv[1] == 'yellow'):
      yellow.turn_on()

  if (sys.argv[2] == 'off'):

    if (sys.argv[1] == 'red'):
      red.turn_off()

    if (sys.argv[1] == 'green'):
      green.turn_off()
 
    if (sys.argv[1] == 'yellow'):
      yellow.turn_off()

    if (sys.argv[1] == 'purple'):
      purple.turn_off()


    
# vim:ts=2:sw=2:sts=2:et:ft=python

