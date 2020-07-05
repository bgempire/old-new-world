
def roundVector(vector, decimals):
	result = []
	
	for i in vector:
		result.append(round(i, decimals))
		
	return result