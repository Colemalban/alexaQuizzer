import requests
import json
import random

def authorize(str):
	samp = "TWcgSDN2AjYb3qZMdwk7ymVWE4sXrNV2GZDfR78u"
	url = "https://api.quizlet.com/2.0/search/sets?q=" + str
	headers = {"Authorization": "Bearer TWcgSDN2AjYb3qZMdwk7ymVWE4sXrNV2GZDfR78u"}
	r = requests.get(url, headers = headers)
	return getSets(str, r.text)
	
	#https://api.quizlet.com/2.0/search/sets?q=capital
	#https://api.quizlet.com/2.0/sets/157370892/terms

def getSets(search, text):
	d = json.loads(text)
	group_id = 0
	for object in d['sets']:
		group_id = object['id']
		break
	url2 = "https://api.quizlet.com/2.0/sets/" + str(group_id)
	headers = {"Authorization": "Bearer TWcgSDN2AjYb3qZMdwk7ymVWE4sXrNV2GZDfR78u"}
	r2 = requests.get(url2, headers = headers)
	return {'quiz':getIntermediate(search, r2.text)}
	
def getIntermediate(search, text):
	d = json.loads(text)
	return getQuestions(d['terms'])

def getQuestions(terms):
	myTerms = []
	i = 0
	random.shuffle(terms)
	for term in terms:
		#print(term['definition'])
		myTerms.append({"question": term['term'],"answer": term['definition']})
		i += 1
		if i == 10:
			break
	
	return {"index": 0, "correct": 0, "questions": myTerms}
	
#print(authorize("Spanish"))
