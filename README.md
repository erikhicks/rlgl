rlgl
====

Red Light Green Light



Procedure
===

Day 1

- installed OS on Raspberry pi
    - NOOB, then Raspbian
 
- got LED lights blinking from GPIO

    Create a GPIO file access:
    echo 11 > /sys/class/gpio/export 
    
    Configure the Pin Direction (In/Out):
    echo out > /sys/class/gpio/gpio11/direction
    
    Write a value to turn on the LED using the GPIO11:
    echo 1 > /sys/class/gpio/gpio11/value
    
    Now your led should be ON!!!
    
    Write a value to clear the LED using the GPIO11
    echo 0 > /sys/class/gpio/gpio11/value
    
    Now your led should be OFF!!!
    
    Delete the created GPIO (11)
    echo 11 > /sys/class/gpio/unexport
    
- installed Piface to control relays

- installed node.js to create web interface to control relays

- installed wifi adapter



Day 2


