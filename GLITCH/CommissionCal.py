#!/bin/python

from serial import Serial
import GLITCH_COMMISSION as G

S=Serial(port="/dev/tty.USA49W262P1.1")
S.isOpen()
S.setTimeout(1)

A=Serial(port="/dev/tty.usbmodem411",baudrate=115200)
A.setTimeout(1)

#if( A.isOpen() and S.isOpen()):
if(S.isOpen()):
	#GLITCH.Stress(S,A)
	G.Setup(S)
	print "Ready for operation."
        G.TestDeploy(S,A)
	G.TestRetract(S,A)
