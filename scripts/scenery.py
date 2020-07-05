import bge

from bge.logic import globalDict
from mathutils import Vector, Matrix

ELEVATOR_SPEED = 0.05

def getMultiplier(value):
	return -1 if value < 0 else 1

def addSmoke(cont):
	own = cont.owner
	
	delay = cont.sensors["Delay"]
	
	if delay.positive and not "NoSmoke" in own.groupObject:
		own.scene.addObject("SmokeParticle", own, 180)

def skybox(cont):
	own = cont.owner
	
	always = cont.sensors["Always"]
	
	sky1 = own.scene.objects["Sky1"]
	sky2 = own.scene.objects["Sky2"]
	
	skyboxSpeed = 0.0001
	
	if always.positive:
		
		if "SkyboxSpeed" in own:
			skyboxSpeed = own["SkyboxSpeed"]
		
		if always.status == 1:
			own.scene.active_camera = own
			
		matrix1 = Matrix.Translation((-skyboxSpeed, 0.0, 0.0))
		matrix2 = Matrix.Translation((-skyboxSpeed*2.5, 0.0, 0.0))
		sky1.meshes[0].transformUV(-1, matrix1)
		sky2.meshes[0].transformUV(-1, matrix2)
		
def elevator(cont):
	own = cont.owner
	platform = own.childrenRecursive["ElevatorPlatform"]
	group = own.groupObject
	
	always = cont.sensors["Always"]
	message = cont.sensors["Message"]
	
	if group is None:
		own.endObject()
		return
		
	if "Target" in group and "Id" in group:
		if message.positive:
			for body in message.bodies:
				if body == str(group["Id"]):
					own["Active"] = True
					always.usePosPulseMode = True
	
	if always.positive and own["Active"]:
		distance = round(own.getDistanceTo(platform), 1)
		
		if distance < abs(group["Target"]) and own["AtOrigin"] == 1 or \
			distance > 0 and own["AtOrigin"] == -1:
			movVec = [
				0, 
				0, 
				ELEVATOR_SPEED * getMultiplier(group["Target"]) * own["AtOrigin"]
			]
			platform.applyMovement(movVec, False)
		
		else:
			own["Active"] = False
			own["AtOrigin"] *= -1
			always.usePosPulseMode = False
	
