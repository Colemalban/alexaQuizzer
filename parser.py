import requests
import json
import random

def authorize(key):
	print(key)
	samp = "TWcgSDN2AjYb3qZMdwk7ymVWE4sXrNV2GZDfR78u"
	url = "https://api.quizlet.com/2.0/users/Steven_Davis1/sets?whitespace=1"
	headers = {"Authorization": "Bearer TWcgSDN2AjYb3qZMdwk7ymVWE4sXrNV2GZDfR78u"}
	r = requests.get(url, headers = headers)
	return {'quiz':getSets("Capital", r.text)}
	
def getSets(search, text):
	d = json.loads(text)
	for object in d:
		if search in object['title']:
			return getQuestions(object['terms'])
			break			

def getQuestions(terms):
	myTerms = []
	i = 0
	for term in terms:
		#print(term['definition'])
		myTerms.append({"question": term['term'],"answer": term['definition']})
		i += 1
		if i == 10:
			break
		
	random.shuffle(myTerms)
	return {"index": 0, "correct": 0, "questions": myTerms}
	
