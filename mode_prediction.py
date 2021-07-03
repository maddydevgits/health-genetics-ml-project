
import random

def predict_mode():
	k=(random.randint(1,3))
	if(k==1):
		k='Low'
	elif(k==2):
		k='Medium'
	elif(k==3):
		k='High'
	return(k)