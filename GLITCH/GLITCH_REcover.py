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

def ConvertStep(step):
	step = step.lstrip('^XZ,')
	step = re.sub('(?<=^[\+\-])0+','',step)
	step = step.strip('\r')
        if(step=='+' or step=='-' or step==''):
                step = 0
        else:
                try:
			step = int(step)
		except (ValueError, RuntimeError, TypeError, NameError):
			print "Not valid for integer conversion: ", step

        return step

def GetXZ(portVXM):
	""" Return tuple of X and Z axis positions """
	portVXM.flush()
	portVXM.write("X ")
	posX = portVXM.read(9)
        posX = ConvertStep(posX)	
	portVXM.write("Z ")
	posZ = portVXM.read(9)
        posZ = ConvertStep(posZ)	

	return posX, posZ

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
		xpos=port.read(9)
		print(xpos)
		port.write("R")
		time.sleep(5)
		resp=WaitUntilReady(port)
		count = count+1
		print(count)

def Setup(portVXM):	
        """ Setup VXM, and make sure status 'R' is returned."""
        commandString = "F"
        portVXM.write(commandString)
        commandString = "setMA1M5,setMA3M4 "
	#Set Motor 1 Absolute index
	
	#Set program to stop and send 'O' when limit reached 
        portVXM.write(commandString)
	WaitUntilReady(portVXM)
	portVXM.write("Q")
 
def TestDeploy(portVXM,portArd):
        commandString = "F"
        portVXM.write(commandString)
	Xpos,Zpos = GetXZ(portVXM)
        commandString = "PM-1,C,SA1M400,SA3M400,SA1M400,SA3M400,LM0,I1M50,P5,I3M-400,P5,L0,R,"
        portVXM.write(commandString)
	t0 = time.time() 
	t = time.time() 
	resp=''
        
	while(not('21,0,1\n\r21,1,2\n\r21,0,0\n\r' in resp) and Xpos < 5500):
                resp = portArd.read(1000)
		t = time.time() 
		Xpos,Zpos = GetXZ(portVXM)
		if((t-t0)%100==0):
			sys.stdout.write('\r')
			sys.stdout.write(str(Zpos))
			sys.stdout.flush()
		if(Xpos >= 5450):
			print '\n',"Garage Reel Approaching Limit", '\n'

	portVXM.write("D,")
        resp = portVXM.read(1000)
        resp = (portVXM.read(1000)).rstrip()
	portVXM.write("Q,")
	Xpos, Zpos = GetXZ(portVXM)
        localtime = time.asctime(time.localtime(time.time()))
	print 'Source Fully Deployed at (X,Y) : ',Xpos, '\t', Zpos ,'\t', 'at localtime: ', localtime
	print '\t', abs(t-t0) , '\t', 'Seconds \r'
	portArd.flush()

def TestRetract(portVXM,portArd):
        """ Garage source, and make sure '^' is returned."""
        commandString = "F"
        portVXM.write(commandString)
        commandString = "PM-3,C,SA1M400,SA3M100,LM0,I3M400,P5,I1M-90,P5,L3,R "
        portVXM.write(commandString)
	resp='abs'
	while( '^' not in resp ):
	    resp = portVXM.read(1000)
	
	print "Moving to Standard Operation."	
        commandString = "PM-2,C,SA1M400,SA3M100,LM0,I3M400,P5,I1M-90,P5,L0,R "
        portVXM.write(commandString)
	t0 = time.time() 
	t = time.time() 
	portArd.flushInput()
	resp='abs'
	
        #while( ('21,1,1' not in resp) and ((t-t0)>30.0)):
        while( not('21,0,1\n\r21,1,1\n\r21,0,0\n\r' in resp) ):
	    resp = portArd.read(10000)
	    t = time.time()

	#print "CONDITION: \t" ,('21,1,1' not in resp),'\t'
	portVXM.write("D,")
        resp = portVXM.read(1000)
	Xpos, Zpos = GetXZ(portVXM)
        localtime = time.asctime(time.localtime(time.time()))
	print "Source Fully Retracted at (X,Y) : ",Xpos, "\t", Zpos ,"\t", "at localtime: ", localtime
	print abs(t-t0) , "\t Seconds \r"
	WaitUntilReady(portVXM)
	portVXM.write("C,IA1M-0,IA3M-0,R ")
	portVXM.write("Q, ")
	portArd.flush()

def Stress(portVXM,portArd):
        cycles = 0;
	while(1):
		TestDeploy(portVXM,portArd)
		TestRetract(portVXM,portArd)
 		cycles = cycles + 1
		print "Source deployed and retracted" , cycles

	

