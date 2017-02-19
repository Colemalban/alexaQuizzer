import requests
import json

def authorize():
	samp = "TWcgSDN2AjYb3qZMdwk7ymVWE4sXrNV2GZDfR78u"
	url = "https://api.quizlet.com/2.0/users/Steven_Davis1/sets?whitespace=1"
	headers = {"Authorization": "Bearer TWcgSDN2AjYb3qZMdwk7ymVWE4sXrNV2GZDfR78u"}
	r = requests.get(url, headers = headers)
	getSets("Capital", r.text)
	
def getSets(search, text):
	d = json.loads(text)
	for object in d:
		if search in object['title']:
			getQuestions(object['terms'])
			break			

def getQuestions(terms):
	myTerms = []
	i = 0
	for term in terms:
		#print(term['definition'])
		myTerms.append({"Question": term['term'],"Answer": term['definition']})
		i += 1
		if i == 10:
			break
		
	#print(myTerms)
	return {"index": 0, "correct": 0, "questions": myTerms}
	
authorize()