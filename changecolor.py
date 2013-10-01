#!/usr/bin/env python

import time
import piface.pfio
import sys

piface.pfio.init(False)

red = piface.pfio.LED(0)
green = piface.pfio.LED(1)
yellow = piface.pfio.LED(2)

def all_off():
  red.turn_off()
  green.turn_off()
  yellow.turn_off()

if (len(sys.argv) > 1):

  if (sys.argv[1] == 'red'):
    red.turn_on()
    green.turn_off()
    yellow.turn_off()

  if (sys.argv[1] == 'green'):
    red.turn_off()
    green.turn_on()
    yellow.turn_off()

  if (sys.argv[1] == 'yellow'):
    red.turn_off()
    green.turn_off()
    yellow.turn_on()

  if (sys.argv[1] == 'init'):
    piface.pfio.init()
    green.turn_on()
    time.sleep(1)
    red.turn_on()
    time.sleep(1)
    yellow.turn_on()
    time.sleep(2)
    all_off()

  if (sys.argv[1] == 'off'):
    all_off()
    
# vim:ts=2:sw=2:sts=2:et:ft=python

