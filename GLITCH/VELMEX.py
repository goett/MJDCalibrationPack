# Python module for control of VELMEX stepper motor

from serial import Serial
from time import sleep
import sys

def Clear(port):
	""" Clear current program from VELMEX memory."""
	port.write("C")

def Run(port):
	""" Run current program in VELMEX memory."""
	port.write("R");

def JogMode(port):
	""" Put VELMEX controller offline and leave in jog mode."""
	port.write("Q")

def Online(port):
	""" Put VELMEX controller online and do not echo commands.."""
	port.write("F")

def Index(port,x,y):
	""" Instruct controller to individually move motor x by y and Run"""
	commandString = "C,"+"I"+str(x)+"M"+str(y)+",R"
	port.write(commandString)

def IndexS(port,x,y):
	""" Instruct controller to individually move motor x by y and Run, then sleep for 10 seconds"""
	commandString = "C,"+"I"+str(x)+"M"+str(y)+",R"
	port.write(commandString)
	sleep(5)

def TestSlip(port,N):
	""" Drive motor back and forth across marker source for N interations. Assumes marker is primed BEHIND the drive roller"""
	for its in range(N):
		print "forward iteration " + str(its)
		for i in range(20):
			IndexS(port,2,-400)

		print "backward iteration " + str(its)
		for i in range(20):
			IndexS(port,2,400)


def TestSlipDual(port,N):
	""" Drive motor back and forth across marker source for N interations. Assumes marker is primed BEHIND the drive roller"""
	for its in range(N):
		print "forward iteration " + str(its)
		for i in range(10):
			IndexS(port,1,133)
			IndexS(port,2,-400)

		print "backward iteration " + str(its)
		for i in range(10):
			IndexS(port,1,-133)
			IndexS(port,2,400)


def TestSlipDualReverse(port,N):
	""" Drive motor back and forth across marker source for N interations. Assumes marker is primed BEHIND the drive roller"""
	for its in range(N):
		print "backward iteration " + str(its)
		for i in range(10):
			IndexS(port,1,-133)
			IndexS(port,2,400)

		print "forward iteration " + str(its)
		for i in range(10):
			IndexS(port,1,133)
			IndexS(port,2,-400)

def TestResponse(port):
	""" Make sure '^' is returned."""
	commandString = "F,N"
	port.write(commandString)
	commandString = "F,C,I1M500,I1M-500"
	port.write(commandString)
	port.timeout=2
	port.write("R")
	resp=port.read(100)
	print(resp)
	count=1
	while(resp=='^'):
        	port.write("X")
		xpos=port.read(100)
		print(xpos)
		port.write("R")
		resp=port.read(100)
		count = count+1
		print(count)
 

