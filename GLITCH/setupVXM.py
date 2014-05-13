#!/bin/python

from serial import Serial
import GLITCH

S=Serial(port="/dev/tty.USA49W2624P1.1")
S.isOpen()
S.setTimeout(1)

#A=Serial(port="/dev/tty.usbmodem26241",baudrate=115200)
#A.setTimeout(1)

#if( A.isOpen() and S.isOpen()):
if(S.isOpen()):
	#GLITCH.Stress(S,A)
	GLITCH.Setup(S)
	print "Ready for operation."
