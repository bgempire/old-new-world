import bge

from bge.logic import globalDict, expandPath
from pathlib import Path
from ast import literal_eval

curPath = Path(expandPath("//")).resolve()

# bge.render.setMipmapping(0)

def loadData():
	loadConfig()
	loadLang()
	
def loadConfig():
	configPath = curPath / "config.txt"
	
	try:
		with open(configPath.as_posix(), "r") as openedFile:
			globalDict["Config"] = literal_eval(openedFile.read())
			print("> Loaded config from", configPath.as_posix())
	
	except:
		print("X Could not load config from", configPath.as_posix())
	
def loadLang():	
	path = Path(expandPath('//lang/')).resolve()
	globalDict['Lang'] = {}
	
	for _file in path.iterdir():
		if _file.suffix == '.txt':
			try:
				globalDict['Lang'][_file.stem] = literal_eval(_file.open(encoding='utf_8').read())
				print('> Language read from:', _file.name)
				
			except:
				print('X Could not read language:', _file.name)
	
loadData()