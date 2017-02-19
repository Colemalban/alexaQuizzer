from flask import Flask,request,jsonify
from OpenSSL import SSL

context = SSL.Context(SSL.SSLv23_METHOD)

app = Flask(__name__)

quiz = {
	"index":0,
	"correct":0,
	"questions":[
		{'question':'what is the capital of maryland','answer':'annapolis'},{'question':'What is the capital of USA','answer':'DC'}
	]
}

#Will check if this is an answer
def is_answer():
	quiz = get_current_quiz()
	if(quiz['index'] < len(quiz['questions'])):
		return True
	else:
		return False

#This will tell if this is for a new quiz
def is_start_quiz():
	return request.get_json()['request']['intent']['name'] == 'StartQuiz'

#This will tell if the request is for a new session
def is_new_session():
	return request.get_json()['session']['new'] == True

#This will tell if the request is a new intent request
def is_intent_req():
	return request.get_json()['request']['type'] == 'IntentRequest'

#This will tell if the request is for a new quiz
def new_quiz():
	return is_new_session() and is_intent_req()  and is_start_quiz()

#Get current quiz from session object
def get_current_quiz():
	return request.get_json()['session']['attributes']['quiz']

#Will check if the given anwer is correct and respond accordingly
def check_if_correct(quiz,answer):
	question = quiz['questions'][quiz['index']]
	result = answer in question['answer']
	quiz['index'] = quiz['index'] + 1
	quiz['correct'] = quiz['correct'] + 1	
	return (quiz, result)

def is_quiz_over(quiz):
	return quiz['index'] >= len(quiz['questions'])	

#Generate a new quiz session
def sessionAttr():
	return {'quiz':quiz}

def generate_response():
	json_obj = {}
	json_obj["version"] = "1.0"
	resp = {'outputSpeech':{'type':'PlainText','text':'What is the capital of maryland'}}
	resp['shouldEndSession'] = False
	json_obj['response'] = resp
	return jsonify(json_obj)

def generate_start():
	json_obj = {}
	json_obj["version"] = "1.0"
	resp = {'outputSpeech':{'type':'PlainText','text':'Lets begin. '+quiz['questions'][0]['question']}}
	json_obj['sessionAttributes'] = sessionAttr()
	resp['shouldEndSession'] = False 
	json_obj['response'] = resp
	return jsonify(json_obj)

#This will extract the user answer from the request
def get_user_answer():
	return "cole"

#produce a result string depending if the answer was correct or not
def parse_result(result):
	if(result):
		return "That was correct."
	else:
		return "That was incorrect."

def end_quiz():
	json_obj = {}
	json_obj["version"] = "1.0"
	resp = {'outputSpeech':{'type':'PlainText','text':'Game over'}}
	resp['shouldEndSession'] = True
	json_obj['response'] = resp
	return jsonify(json_obj)

def next_question():
	quiz = get_current_quiz()
	answer = get_user_answer()
	quiz,result = check_if_correct(quiz)
	result_string = parse_result(result)
	if(is_quiz_over(quiz)):
		return end_quiz()
	json_obj = {}
	json_obj["version"] = "1.0"
	resp = {'outputSpeech':{'type':'PlainText','text':result_string+' Next question. '+quiz['questions'][quiz['index']]['question']}}
	json_obj['sessionAttributes'] = {'quiz':quiz}
	resp['shouldEndSession'] = False 
	json_obj['response'] = resp
	return jsonify(json_obj)
	
@app.route('/',methods=['GET'])
def quizlet_auth():
	code = request.args.get('code')
	return jsonify({'code':code})

@app.route("/",methods=['POST'])
def test():
	if(new_quiz()):
		return generate_start()
	elif(is_answer()):
		return next_question()
	else:
		return end_quiz()

app.run(host='0.0.0.0',port="443",debug=False,ssl_context=('cert.pem','key.pem'))
