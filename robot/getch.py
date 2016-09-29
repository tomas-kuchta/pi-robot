# This is blocking (meaning waiting for key press) implementation
# for getting single character out of stdin/terminal/console

import os
import sys    
import termios
import fcntl

class _Getch:
	"""Gets a single character from standard input.  Does not echo to the screen."""
	def __init__(self):
		try:
			self.impl = _GetchWindows()
		except ImportError:
			self.impl = _GetchUnix()
	def __call__(self): 
		char = self.impl()
		if char == '\x03':
			raise KeyboardInterrupt
		elif char == '\x04':
			raise EOFError
		return char

class _GetchUnix:
	def __init__(self):
		import tty
		import sys
	def __call__(self):
		import sys
		import tty
		import termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch


class _GetchWindows:
	def __init__(self):
		import msvcrt
	def __call__(self):
		import msvcrt
		return msvcrt.getch()

getch = _Getch()

# Older implementation which did not worked reliably
if False:
	def getch():
		fd = sys.stdin.fileno()
		
		oldterm = termios.tcgetattr(fd)
		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)
		
		oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
		
		try:        
			while 1:            
				try:
					c = sys.stdin.read(1)
					break
				except IOError: pass
		finally:
			termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
			fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
		return(c)

# Previous implementation is blocking in python3 and requires 'Enter' press in python 2.7
# Following code presents non blocking behaviour in Linux using python 3 and 2.7
# Recommended usage:
# import getch
# # Set terminal to non blocking mode
# getch.initNonBlockingStdinRead()
# # Wait until 'q' key press
# while getch.getchNonBlocking() != 'q':
# 	# do something, anything
# 	time.sleep(0.01)
# # restore terminal settings to normal line mode
# getch.restoreStdinRead()

import sys, termios, tty, select, time

getch_nonBlockingInitDone = 0

def isData():
	# Returns 1 if there are data waiting in stdin else 0 
	return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def initNonBlockingStdinRead():
	# set stdin tty to non-blocking read
	global getch_nonBlockingInitDone, getch_oldStdinTtySettings
	if getch_nonBlockingInitDone == 0:
		getch_oldStdinTtySettings = termios.tcgetattr(sys.stdin)
		tty.setcbreak(sys.stdin.fileno())
		getch_nonBlockingInitDone = 1
	else:
		print("WARNING: initNonBlockingStdinRead: stdin tty already initialized")

def restoreStdinRead():
	# set stdin tty to non-blocking read
	global getch_nonBlockingInitDone, getch_oldStdinTtySettings
	if getch_nonBlockingInitDone == 1:
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, getch_oldStdinTtySettings)
		getch_nonBlockingInitDone = 0
	else:
		print("WARNING: restoreStdinRead: stdin tty is not set to non blocking mode")

def getchNonBlocking():
	if getch_nonBlockingInitDone:
		if isData():
			c = sys.stdin.read(1)
			return c
		else:
			return ""
	else:
		print("WARNING: restoreStdinRead: stdin tty is not set to non blocking mode. If needed, set it by initNonBlockingStdinRead(). Waiting for 'Enter'")
		c = sys.stdin.read(1)
		return c



