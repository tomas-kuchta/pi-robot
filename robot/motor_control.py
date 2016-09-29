import time
import getch
import atexit
useMotors = True
if useMotors:
	from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

# Constants
lMotorAdjust = 0       # motor speed adjustment to match other motors (for future implementation)
rMotorAdjust = 0       # motor speed adjustment to match other motors (for future implementation)
maxSpeed = 255         # 1-255 (depending on motor control circuitry)
maxAccelRate = 1000    # maximum acceleration rate (used for emergency stops, etc.)
speedIncrStep = 150    # speed increase per key press
accelRate = 1000       # acceleration rate [speed increase per second]
turnIncrStep = 20      # turn left/Right speed deferential per key press (speed of turning)
turnZeroIncrStep = 110 # turn left/Right speed deferential per key press when starting from stop (speed of turning from zero)
turnAccelRate = 1000   # turn acceleration rate

# Control keys:
#useControlKeys = "vi"
#useControlKeys = "minecraft"
useControlKeys = "arrows"
if useControlKeys == "vi":
	keyRight = "j"
	keyLeft = ";"
	keyForward = "k"
	keyReverse = "l"
elif useControlKeys == "minecraft":
	keyRight = "d"
	keyLeft = "a"
	keyForward = "w"
	keyReverse = "s"
elif useControlKeys == "arrows":
	keyRight = "\x1b[D"
	keyLeft = "\x1b[C"
	keyForward = "\x1b[A"
	keyReverse = "\x1b[B"
else:
	print("ERROR: Unknown useControlKeys: $s Exitting..." % useControlKeys)
	exit(1)
keyStop = " "
keyExit = "q"

# Initializing variables
currentSpeedL = 0    # holds current speed left
currentSpeedR = 0    # holds current speed right
targetSpeedL = 0     # target speed to accelerate to (current speed will accelerate to target speed)
targetSpeedR = 0     # target speed to accelerate to (current speed will accelerate to target speed)

# create a default object, no changes to I2C address or frequency
if useMotors: 
      mh = Adafruit_MotorHAT(addr=0x60)
      myMotor = {}
      myMotor['l'] = mh.getMotor(2)
      myMotor['r'] = mh.getMotor(1)
	
# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
	global useMotors, mh
	print("Turning off all DC motors")
	if useMotors:
		mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
		mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
		mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
		mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

def initMotors():
	global useMotors, mh, myMotor
	global speedIncrStep
	print("Initializing motors ...")
	if useMotors:
		atexit.register(turnOffMotors)
		myMotor['l'].setSpeed(speedIncrStep)
		myMotor['r'].setSpeed(speedIncrStep)
		myMotor['l'].run(Adafruit_MotorHAT.FORWARD)
		myMotor['r'].run(Adafruit_MotorHAT.FORWARD)
		myMotor['l'].run(Adafruit_MotorHAT.RELEASE)
		myMotor['r'].run(Adafruit_MotorHAT.RELEASE)

def shutdownMotors():
	global useMotors, mh, myMotor
	print("Shutting down motors ...")
	if useMotors:
		myMotor['l'].run(Adafruit_MotorHAT.RELEASE)
		myMotor['r'].run(Adafruit_MotorHAT.RELEASE)

def accelerate(interruptKeyLst=(), mode="normal"):
	global lMotorAdjust, rMotorAdjust
	global maxSpeed, maxAccelRate, accelRate, turnAccelRate
	global currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR
	global useMotors, mh, myMotor
	debug = 2
	enableInterupt = False
	modeLst=("normal", "fast")
	#if debug: print("Accelerating L: %d --> %d  R: %d --> %d at %s acceleration rate." % (currentSpeedL, targetSpeedL, currentSpeedR, targetSpeedR, mode))
	#currentSpeedL, currentSpeedR = targetSpeedL, targetSpeedR; return ""
	if enableInterupt:
		setCharModeStdinLocally = 0
		if not getch.getch_nonBlockingInitDone:
			getch.initNonBlockingStdinRead()
			setCharModeStdinLocally = 1
	if not mode in modeLst:
		print("ERROR: accelerate : Invalid mode argument %s. Use one of: %s" % (mode, modeLst))
		exit(1)
	if mode == "normal":
		accelTimeStep = 1.0 / accelRate
		turnAcellTimeStep = 1.0 / turnAccelRate
	else:
		accelTimeStep = 1.0 / maxAccelRate
		turnAcellTimeStep = 1.0 / maxAccelRate	
	if enableInterupt and len(interruptKeyLst) != 0:
		keyPress = getch.getchNonBlocking()
	else:
		keyPress = ""
	if debug: print("Accelerating L: %d --> %d  R: %d --> %d at %s acceleration rate." % (currentSpeedL, targetSpeedL, currentSpeedR, targetSpeedR, mode))
	# forward/reverse/left/right
	while (keyPress == "" or not keyPress in interruptKeyLst) and (currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR):
		if currentSpeedL != targetSpeedL:
			# left motor
			if currentSpeedL > 0:
				# forward
				if currentSpeedL > targetSpeedL:
					# forward slow down
					currentSpeedL -= 1
					if debug >= 3: print("  left motor forward slow down (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
				else:
					# currentSpeedL < targetSpeedL:
					# forward speed up
					currentSpeedL += 1
					if debug >= 3: print("  left motor forward speed up (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
			elif currentSpeedL < 0:
				# reverse
				if currentSpeedL > targetSpeedL:
					# reverse speed up
					currentSpeedL -= 1
					if debug >= 3: print("  left motor reverse speed up (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
				else:
					# currentSpeedL < targetSpeedL:
					# reverse slow down
					currentSpeedL += 1
					if debug >= 3: print("  left motor reverse slow down (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
			else:
				# must be starting from 0 accelerating forward/reverse (crossing 0 speed)
				if currentSpeedL > targetSpeedL:
					# forward slow down
					currentSpeedL -= 1
					if debug >= 2: print("  0 to reverse left motor speed up (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
					if useMotors: myMotor['l'].run(Adafruit_MotorHAT.BACKWARD)
				else:
					# currentSpeedL < targetSpeedL:
					# forward speed up
					currentSpeedL += 1
					if debug >= 2: print("  0 to forward left motor speed up( %d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))				
					if useMotors: myMotor['l'].run(Adafruit_MotorHAT.FORWARD)
			if useMotors: myMotor['l'].setSpeed(abs(currentSpeedL))
		if currentSpeedR != targetSpeedR:
			# right motor
			if currentSpeedR > 0:
				# forward
				if currentSpeedR > targetSpeedR:
					# forward slow down
					currentSpeedR -= 1
					if debug >= 3: print("  right motor forward slow down (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
				else:
					# currentSpeedR < targetSpeedR:
					# forward speed up
					currentSpeedR += 1
					if debug >= 3: print("  right motor forward speed up (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
			elif currentSpeedR < 0:
				# reverse
				if currentSpeedR > targetSpeedR:
					# reverse speed up
					currentSpeedR -= 1
					if debug >= 3: print("  right motor reverse speed up (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
				else:
					# currentSpeedR < targetSpeedR:
					# reverse slow down
					currentSpeedR += 1
					if debug >= 3: print("  right motor reverse slow down (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
			else:
				# must be starting from 0 accelerating forward/reverse (crossing 0 speed)
				if currentSpeedR > targetSpeedR:
					# forward slow down
					currentSpeedR -= 1
					if debug >= 2: print("  0 to reverse right motor speed up (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
					if useMotors: myMotor['r'].run(Adafruit_MotorHAT.BACKWARD)
				else:
					# currentSpeedR < targetSpeedR:
					# forward speed up
					currentSpeedR += 1
					if debug >= 2: print("  0 to forward right motor speed up (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))				
					if useMotors: myMotor['r'].run(Adafruit_MotorHAT.FORWARD)
			if useMotors: myMotor['r'].setSpeed(abs(currentSpeedR))
			#currentSpeedL = targetSpeedL
			#lllcurrentSpeedR = targetSpeedR
			time.sleep(accelTimeStep)
		#if debug: print("  Waiting for keyPress")
		if enableInterupt and len(interruptKeyLst) != 0: keyPress = getch.getchNonBlocking()
		#if debug: print("  keyPress: %s" % keyPress)
		#if debug: print("  loop(%d,%d) --> (%d,%d) " % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR), (currentSpeedL != targetSpeedL and currentSpeedR != targetSpeedR))
	if enableInterupt and setCharModeStdinLocally: getch.restoreStdinRead()
	if debug: print("  return %s; (%d,%d) --> (%d,%d)" % (keyPress, currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
	return keyPress

def goForward (doNotAccelerate=False):
	global currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR, maxSpeed
	global speedIncrStep
	debug=True
	if doNotAccelerate:
		localSpeedIncrStep = 0
	else:
		localSpeedIncrStep = speedIncrStep
	if currentSpeedL != currentSpeedR:
		lrAverage = (currentSpeedL + currentSpeedR) / 2
	else:
		lrAverage = currentSpeedL
	targetSpeedL = lrAverage + localSpeedIncrStep
	targetSpeedR = lrAverage + localSpeedIncrStep
	if targetSpeedL > maxSpeed: 
		targetSpeedL = maxSpeed
		targetSpeedR = maxSpeed
	if debug: print("goForward: (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
	if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR: accelerate()
def goReverse (doNotAccelerate=False):
	global currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR, maxSpeed
	global speedIncrStep, turnZeroIncrStep
	debug=True
	if doNotAccelerate:
		localSpeedIncrStep = 0
	else:
		localSpeedIncrStep = speedIncrStep
	if currentSpeedL != currentSpeedR:
		lrAverage = (currentSpeedL + currentSpeedR) / 2
	else:
		lrAverage = currentSpeedL
	targetSpeedL = lrAverage - localSpeedIncrStep
	targetSpeedR = lrAverage - localSpeedIncrStep
	if targetSpeedL < -maxSpeed: 
		targetSpeedL = -maxSpeed
		targetSpeedR = -maxSpeed
	if debug: print("goReverse: (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
	if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR: accelerate()
def goLeft (localTurnIncrStep=turnIncrStep):
	global currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR, maxSpeed
	#global turnIncrStep, turnZeroIncrStep
	debug=True
	targetSpeedL = currentSpeedL - localTurnIncrStep
	targetSpeedR = currentSpeedR + localTurnIncrStep
	# do not exceed maxSpeed - find turning speed increment not exceeding maxSpeed
	if targetSpeedL < -maxSpeed:
		targetSpeedL = -maxSpeed
	elif targetSpeedL > maxSpeed:
		targetSpeedL = maxSpeed
	if targetSpeedR < -maxSpeed:
		targetSpeedR = -maxSpeed
	elif targetSpeedR > maxSpeed:
		targetSpeedR = maxSpeed
	if debug: print("goLeft: (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
	if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR: accelerate()
def goRight(localTurnIncrStep=turnIncrStep):
	global currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR, maxSpeed
	#global turnIncrStep
	debug=True
	targetSpeedL = currentSpeedL + localTurnIncrStep
	targetSpeedR = currentSpeedR - localTurnIncrStep
	# do not exceed maxSpeed - find turning speed increment not exceeding maxSpeed
	if targetSpeedL < -maxSpeed:
		targetSpeedL = -maxSpeed
	elif targetSpeedL > maxSpeed:
		targetSpeedL = maxSpeed
	if targetSpeedR < -maxSpeed:
		targetSpeedR = -maxSpeed
	elif targetSpeedR > maxSpeed:
		targetSpeedR = maxSpeed
	if debug: print("goRight: (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
	if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR: accelerate()
def goStop():
	global currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR, maxSpeed
	global speedIncrStep
	debug=True
	targetSpeedL = 0
	targetSpeedR = 0
	if debug: print("goStop: (%d,%d) --> (%d,%d)" % (currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR))
	if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR: accelerate()

def getKeyboardCharacter():
	# Returns keyboard character or characters in case of multiple char control sequences.
	# This function is wrapper around getch.getch()
	# for transparent handling multiple character sequences like:
	# direction arrows: \x1b[A \x1b[B \x1b[C \x1b[D ....
	charSt = 1
	arrowChar1St = 2
	arrowChar2St = 3
	exitSt = 4
	localState = charSt
	retKey = ""
	while localState != exitSt:
		localKey = getch.getch()
		if localState == charSt:
			if localKey == "\x1b":
				retKey = retKey + localKey
				localState = arrowChar1St
			else:
				retKey = localKey
				localState = exitSt
		elif localState == arrowChar1St:
			if localKey == "[":
				retKey = retKey + localKey
				localState = arrowChar2St
			else:
				print("ERROR: getControlCharacter: Expecting character '[' after control char '\x1b', got: %s Exitting....\n" % localKey)
				exit(1)
		elif localState == arrowChar2St:
			retKey = retKey + localKey
			localState = exitSt
		else:
			print("ERROR: getControlCharacter: Unknown state %s Exitting....\n" % localSt)
			exit(1)
	return retKey

def main():
	global lMotorAdjust, rMotorAdjust
	global maxSpeed, maxAccelRate, speedIncrStep, accelRate, turnIncrStep, turnZeroIncrStep, turnAccelRate
	global keyRight, keyLeft, keyForward, keyReverse, keyStop, keyExit
	global currentSpeedL, currentSpeedR, targetSpeedL, targetSpeedR
	global mh, myMotor
	
	debug = True
	state = "stopSt"  # initial FSM state
	key = ""
	doNotAccelerate = True
	print(state)
	
	initMotors()
	
	while key != keyExit:
		if debug: print("State: %s, key: %s" % (state, key))
		if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR:
			key = accelerate((keyStop))
		if state == "stopSt":
			# motors stop in this state
			if currentSpeedL != 0 or currentSpeedR !=0:
				goStop()
			#else:
			#	key = getch.getch()
			if key == keyRight:
				goRight(turnZeroIncrStep)
				state = "turnSt"
				print("Go to: ", state)
			elif key == keyLeft:
				goLeft(turnZeroIncrStep)
				state = "turnSt"
				print("Go to: ", state)
			elif key == keyForward:
				goForward()
				state = "forwardSt"
				print("Go to: ", state)
			elif key == keyReverse:
				goReverse()
				state = "reverseSt"
				print("Go to: ", state)
			elif key == keyExit:
				goStop()
				state = "exitSt"
				print("Go to: ", state)
			if key == keyStop and currentSpeedL != 0 and currentSpeedR !=0:
				# go fast
				goStop()
		elif state == "turnSt":
			# turning in place
			#if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR:
			#	key = accelerate((keyStop))
			#key = getch.getch()
			if key == keyRight:
				goRight()
				print("Accelerating right, ", state)
			elif key == keyLeft:
				goLeft()
				print("Accelerating left, ", state)
			elif key == keyForward:
				goForward()
				state = "forwardSt"
				print("Go to: ", state)
			elif key == keyReverse:
				goReverse()
				state = "reverseSt"
				print("Go to: ", state)
			elif key == keyExit:
				goStop()
				state = "exitSt"
				print("Go to: ", state)
			elif key == keyStop:
				goStop()
				state = "stopSt"
				print("Go to: ", state)
			if currentSpeedL == targetSpeedL and currentSpeedR == targetSpeedR:
				if currentSpeedL == 0 and currentSpeedR == 0:
					state = "stopSt"
					print("Go to: ", state)
				elif (currentSpeedL +  currentSpeedR)/2 < 0:
					state = "reverseSt"
					print("Go to: ", state)
				elif (currentSpeedL +  currentSpeedR)/2 > 0:
					state = "forwardSt"
					print("Go to: ", state)
		elif state == "turnForwardSt":
			# turning while going forward
			#if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR:
			#	key = accelerate((keyStop))
			if key == keyRight:
				goRight()
				print("Accelerating right, ", state)
			elif key == keyLeft:
				goLeft()
				print("Accelerating left, ", state)
			elif key == keyForward:
				goForward(doNotAccelerate)
				state = "forwardSt"
				print("Go to: ", state)
			elif key == keyReverse:
				goReverse(doNotAccelerate)
				state = "reverseSt"
				print("Go to: ", state)
			elif key == keyExit:
				goStop()
				state = "exitSt"
				print("Go to: ", state)
			elif key == keyStop:
				goStop()
				state = "stopSt"
				print("Go to: ", state)
			if currentSpeedL == targetSpeedL and currentSpeedR == targetSpeedR:
				if currentSpeedL == currentSpeedR:
					if currentSpeedL == 0:
						state = "stopSt"
						print("Go to: ", state)
					elif currentSpeedL > 0:
						state = "forwardSt"
						print("Go to: ", state)
					else:
						state = "reverseSt"
						print("Go to: ", state)
			#key = getch.getch()
		elif state == "turnReverseSt":
			# turning while going in reverse
			#if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR:
			#	key = accelerate((keyStop))
			if key == keyRight:
				goRight()
				print("Accelerating right, ", state)
			elif key == keyLeft:
				goLeft()
				print("Accelerating left, ", state)
			elif key == keyForward:
				goForward(doNotAccelerate)
				state = "forwardSt"
				print("Go to: ", state)
			elif key == keyReverse:
				goReverse(doNotAccelerate)
				state = "reverseSt"
				print("Go to: ", state)
			elif key == keyExit:
				goStop()
				state = "exitSt"
				print("Go to: ", state)
			elif key == keyStop:
				goStop()
				state = "stopSt"
				print("Go to: ", state)
			if currentSpeedL == targetSpeedL and currentSpeedR == targetSpeedR:
				if currentSpeedL == currentSpeedR:
					if currentSpeedL == 0:
						state = "stopSt"
						print("Go to: ", state)
					elif currentSpeedL > 0:
						state = "forwardSt"
						print("Go to: ", state)
					else:
						state = "reverseSt"
						print("Go to: ", state)
			#key = getch.getch()
		elif state == "forwardSt":
			# moving straight forward
			#if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR:
			#	key = accelerate((keyStop))
			if key == keyRight:
				goRight()
				state = "turnForwardSt"
				print("Go to: ", state)
			elif key == keyLeft:
				goLeft()
				state = "turnForwardSt"
				print("Go to: ", state)
			elif key == keyReverse:
				goReverse()
				print("Slowing down, ", state)
			elif key == keyExit:
				goStop()
				state = "exitSt"
				print("Go to: ", state)
			elif key == keyStop:
				goStop()
				state = "stopSt"
				print("Go to: ", state)
			elif key == keyForward:
				goForward()
				print("Accelerating, ", state)
			if currentSpeedL == targetSpeedL and currentSpeedR == targetSpeedR:
				if currentSpeedL == currentSpeedR:
					if currentSpeedL == 0:
						state = "stopSt"
						print("Go to: ", state)
					elif currentSpeedL < 0:
						state = "reverseSt"
					print("Go to: ", state)
			#key = getch.getch()
		elif state == "reverseSt":
			# moving straight in reverse
			#if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR:
			#	key = accelerate((keyStop))
			if key == keyRight:
				goRight()
				state = "turnReverseSt"
				print("Go to: ", state)
			elif key == keyLeft:
				goLeft()
				state = "turnReverseSt"
				print("Go to: ", state)
			elif key == keyForward:
				goForward()
				print("Slowing down, ", state)
			elif key == keyExit:
				goStop()
				state = "exitSt"
				print("Go to: ", state)
			elif key == keyStop:
				goStop()
				state = "stopSt"
				print("Go to: ", state)
			elif key == keyReverse:
				goReverse() 
				print("Accelerating, ", state)
			if currentSpeedL == targetSpeedL and currentSpeedR == targetSpeedR:
				if currentSpeedL == currentSpeedR:
					if currentSpeedL == 0:
						state = "stopSt"
						print("Go to: ", state)
					elif currentSpeedL > 0:
						state = "forwardSt"
						print("Go to: ", state)
			#key = getch.getch()
		elif state == "exitSt":
			shutdownMotors()
			break
		else:
			print("ERROR: Unknown state %s Exiting ....." % state)
			exit(1)
		if currentSpeedL != targetSpeedL or currentSpeedR != targetSpeedR:
			key = accelerate((keyStop))
		key = getKeyboardCharacter()
	shutdownMotors()
	print(state)

main()
