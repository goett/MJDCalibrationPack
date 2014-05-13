#!/bin/python
from serial import Serial
import GLITCH

S=Serial(port="/dev/tty.USA49W2623P1.1")
S.isOpen()
S.setTimeout(1)

S.write("F")
GLITCH.TestResponse(S)
