import bge

from bge.logic import globalDict
from pprint import pformat
from ast import literal_eval

from .utils import roundVector

DEFAULT_PLAYER = {
	"CurPlayer" : "Astronaut",
	"CurPosAstronaut" : [0, 0, 0],
	"CurPosRobot" : [0, 0, 0],
	"CurDirX" : 1,
	"CurDirY" : 0,
	"RobotUnlocked" : False,
	"Map" : {}
}

ASTRONAUT_MOV_SPEED = 0.070
ROBOT_MOV_SPEED = 0.08

if not "Player" in globalDict.keys():
	globalDict["Player"] = DEFAULT_PLAYER

def main(cont):
	own = cont.owner
	group = own.groupObject
	camera = own.scene.active_camera
	
	always = cont.sensors["Always"]
	
	player = globalDict["Player"]
	
	if group is None:
		own.endObject()
		return
		
	if always.status == 1:
		addSkybox(cont)
	
	if always.positive and own["Player"] == player["CurPlayer"] and "Timer" in camera:
		
		processCollision(cont)
		if camera["Timer"] > 0: processInput(cont)
		processAnim(cont)
		if camera["Timer"] > 0: processMovement(cont)
		if camera["Timer"] > 0: debugPlayer(cont)

def addSkybox(cont):
	skyboxAdded = False
	
	for scn in bge.logic.getSceneList():
		if scn.name == "Skybox":
			skyboxAdded = True
			break
			
	if not skyboxAdded:
		bge.logic.addScene("Skybox", 0)

def processCollision(cont):
	own = cont.owner
	player = globalDict["Player"]
	
	collision = cont.sensors["Collision"]
	
	if collision.positive:
		for obj in collision.hitObjectList:
			
			if "Terminal" in obj:
				
				if "Id" in obj.groupObject and "Target" in obj.groupObject:
					own["CollidingObj"] = obj.groupObject
					own["CollidingWith"] = "[\"Terminal\", [\"" + \
						obj.groupObject["Target"] + "\", " + \
						str(obj.groupObject["Id"]) + "]]"
					break
			
			if "Checkpoint" in obj:
				own["LastCheckpoint"] = obj.groupObject
				
				if "UnlockRobot" in own["LastCheckpoint"]:
					player["RobotUnlocked"] = True
					own.sendMessage("RobotUnlocked")
					
				if "FinishGame" in own["LastCheckpoint"]:
					own.sendMessage("FinishGame")
				break
			
			if "Saw" in obj:
				if not "LastCheckpoint" in own:
					own.worldPosition = own.groupObject.worldPosition
				else:
					own.worldPosition = own["LastCheckpoint"].worldPosition
				break
				
			else:
				own["CollidingWith"] = ""
				own["CollidingObj"] = None

def processInput(cont):
	own = cont.owner
	controls = {}
	
	if not "Controls" in own:
		for key in globalDict["Config"].keys():
			if key.startswith("Key"):
				try:
					controls[key] = eval("bge.events." + globalDict["Config"][key])
				except:
					print("X Key", globalDict["Config"][key], " for ", key, "is not valid!")
				
		own["Controls"] = controls
		
	else:
		events = bge.events
		kb = bge.logic.keyboard.events
		player = globalDict["Player"]
		camera = own.scene.active_camera
		
		controls = own["Controls"]
		
		keyUp = kb[controls["KeyUp"]] == 2
		keyDown = kb[controls["KeyDown"]] == 2
		keyLeft = kb[controls["KeyLeft"]] == 2
		keyRight = kb[controls["KeyRight"]] == 2
		keyUse = kb[controls["KeyUse"]] == 1
		keySwitch = kb[controls["KeySwitch"]] == 1
		keyQuit = kb[controls["KeyQuit"]] == 1
		keyRestart = kb[controls["KeyRestart"]] == 1
		
		if keyQuit:
			own.sendMessage("FinishGame")
			
		if keyRestart:
			own.scene.restart()
		
		if keySwitch and player["RobotUnlocked"] and camera["Timer"] > 0:
			player["CurDirX"] = 0
			player["CurPlayer"] = "Astronaut" if player["CurPlayer"] == "Robot" else "Robot"
			newCameraParent = own.scene.objects[player["CurPlayer"]+"CameraAxis"]
			own.childrenRecursive["CameraAxis"].setParent(newCameraParent)
			newCameraParent.childrenRecursive["CameraAxis"].localPosition = [0, 0, 0]
			camera["Timer"] = -0.5
			return
			
		if keyUse:
			colData = [None, None]
			colObj = None
			
			try:
				colData = literal_eval(own["CollidingWith"])
				colObj = own["CollidingObj"]
			except:
				pass
				
			if colData[0] == "Terminal" and colObj is not None:
				own.sendMessage(str(colData[1][0]), str(colData[1][1]))
				colObj.groupMembers["TerminalMesh"]["State"] = "Activated"
			
		if not (keyUp and keyDown) or (keyUp and keyDown):
			player["CurDirY"] = 0
		
		if keyUp and not keyDown:
			player["CurDirY"] = 1
			
		if not keyUp and keyDown:
			player["CurDirY"] = -1
		
		if not (keyRight and keyLeft) or (keyRight and keyLeft):
			player["CurDirX"] = 0
		
		if keyRight and not keyLeft:
			player["CurDirX"] = 1
			
		if not keyRight and keyLeft:
			player["CurDirX"] = -1

def processAnim(cont):
	own = cont.owner
	player = globalDict["Player"]
	armatureAstronaut = own.scene.objects["AstronautArmature"]
	
	if player["CurPlayer"] == "Astronaut":
		
		if player["CurDirX"] != 0:
			armatureAstronaut.playAction("Astronaut", 1, 22, blendin=2, play_mode=1)
			armatureAstronaut.actuators["Track"].object = own.scene.objects[player["CurPlayer"]+"Dir"+str(player["CurDirX"])]
			
		else:
			armatureAstronaut.playAction("Astronaut", 30, 70, blendin=2, play_mode=1)
			
	elif player["CurPlayer"] != "Astronaut":
		armatureAstronaut.playAction("Astronaut", 30, 70, blendin=2, play_mode=1)
	
def processMovement(cont):
	own = cont.owner
	player = globalDict["Player"]
	
	movVec = [0, 0, 0]
	
	if own["Player"] == "Astronaut":
		movVec = [
			ASTRONAUT_MOV_SPEED * player["CurDirX"],
			0,
			0
		]
	
	elif own["Player"] == "Robot":
		movVec = [
			ROBOT_MOV_SPEED * player["CurDirX"],
			0,
			ROBOT_MOV_SPEED * player["CurDirY"]
		]
		
	own.applyMovement(movVec, False)

def debugPlayer(cont):
	own = cont.owner
	
	# Make the debug text visible and set 
	own.scene.objects["DebugText"].visible = globalDict["Config"]["Debug"]
	own.scene.objects["DebugText"].text = pformat(globalDict["Player"], width=10)