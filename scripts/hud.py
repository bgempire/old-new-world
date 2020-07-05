import bge

from bge.logic import globalDict, expandPath
from pprint import pformat

def text(cont):
	pass

def switchLang(scene):
	if globalDict['Config']['Lang'] == 'Português':
		globalDict['Config']['Lang'] = 'English'
		
	else:
		globalDict['Config']['Lang'] = 'Português'
		
	scene.restart()
	
	with open(expandPath('//config.txt'), 'w') as openedFile:
		openedFile.write(str(globalDict['Config']))
		print('Saved config to', openedFile.name)

def widget(cont):
	
	own = cont.owner
	scene = own.scene
	camera = scene.active_camera
	
	over = cont.sensors['Over']
	lmb = cont.sensors['LMB']
	
	game_path = expandPath('//Intro.blend')
	
	if not over.positive:
		own.color[3] = 0.7
	
	if over.positive:
		own.color[3] = 0.9
		
		if own.groupObject and lmb.positive:
			
			if 'Command' in own.groupObject:
				commands = own.groupObject['Command'].split(' | ')
				for command in commands:
					try:
						exec(command)
					
					except:
						print('X Cannot eval expression:', command)