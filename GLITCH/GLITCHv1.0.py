# Python module for control of VELMEX stepper motor

from serial import Serial
import time
import sys
import re

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
	time.sleep(5)

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

def WaitUntilReady(port):
	port.setTimeout(1)
	port.write("V")
        resp=port.read(100)
	while( not( ('^' in resp) or ('R' in resp) ) ):
		port.write("V")
		resp = port.read(1000)

	return resp

def TestResponse(port):
	""" Make sure '^' is returned."""
	commandString = "F"
	port.write(commandString)
	commandString = "PM3,C,I1M500,I3M-500,I3M500,I1M-500,R"
	port.write(commandString)
	WaitUntilReady(port)
	port.write("R")
	resp=WaitUntilReady(port)
	count=0
	print("starting loop:")
	while('^' in resp):
        	port.write("X")
		xpos=port.read(100)
		print(xpos)
		port.write("R")
		time.sleep(5)
		resp=WaitUntilReady(port)
		count = count+1
		print(count)
 
def TestDeploy(portVXM,portArd):
        """ Deploy source, and make sure '^' is returned."""
        commandString = "F"
        portVXM.write(commandString)
        commandString = "setMA1M5,setMA3M4,"
        portVXM.write(commandString)
        commandString = "SA1M200,SA3M200,"
        #portVXM.write(commandString)
        commandString = "PM1,C,LM0,I1M50,P5,I3M-400,P5,L0,R"
        #commandString = "PM1,C,SA1M50,SA3M50,LM0,I1M50,P5,I3M-400,P5,L0,R"
        portVXM.write(commandString)
	resp=''
        while(not('21,1,2' in resp)):
                resp = portArd.read(1000)

	portVXM.write("K")
        resp = portVXM.read(1000)
	portVXM.write("Z")
        resp = (portVXM.read(1000)).rstrip()
	portVXM.write("Q")
        localtime = time.asctime(time.localtime(time.time()))
	print('Source Fully Deployed at : ',resp, 'at localtime: ', localtime)
	portArd.flush()

def TestRetract(portVXM,portArd):
        """ Garage source, and make sure '^' is returned."""
        commandString = "F"
        portVXM.write(commandString)
        commandString = "setMA1M5,setMA3M4,"
        portVXM.write(commandString)
        ## commandString = "SA1M50,SA3M50,"
        ## portVXM.write(commandString)
        ## portVXM.flush()
	## portVXM.write("Z")
	## xxx=portVXM.read(1000)
	## xxx=xxx.rstrip()
	## print("xxx = ",xxx)
        ## print("Z0 is: ",re.sub("-00+","-",xxx))
	## Z0 = float(re.sub("-00+","-",xxx))
        commandString = "PM2,C,SA1M50,SA3M50,LM0,I3M400,P5,I1M-90,P5,L0,R"
        ## commandString = "PM2,C,LM0,I3M400,P5,I1M-90,P5,L0,R,"
        portVXM.write(commandString)
	resp=''
        # while(not('21,1,1' in resp) and not(abs(Z0-Z)<1000)):
        while(not('21,1,1' in resp)):
                resp = portArd.read(1000)
        	# portVXM.flush()
		# portVXM.write("Z")
        	# Z = float(re.sub("-00+","-",(portVXM.read(1000)).rstrip()))
		# print(Zn,'\t',Z)

	portVXM.write("K")
        resp = portVXM.read(1000)
	portVXM.write("Z")
        resp = (portVXM.read(1000)).rstrip()
        localtime = time.asctime(time.localtime(time.time()))
	print('Source Fully Retracted at : ',resp, 'at localtime: ', localtime)
	portVXM.write("C,IA1M-0,IA3M-0,R")
	portVXM.write("Q")
	#print('Source Fully Retracted at : ',resp)
	portArd.flush()

def Stress(portVXM,portArd):
        cycles = 0;
	while(1):
		TestDeploy(portVXM,portArd)
		TestRetract(portVXM,portArd)
 		cycles = cycles + 1
		print "Source deployed and retracted" , cycles

	

