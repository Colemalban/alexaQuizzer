import re
from flask import Flask,request,jsonify
import parser
from OpenSSL import SSL

context = SSL.Context(SSL.SSLv23_METHOD)

app = Flask(__name__)

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
	result =  question['answer'].lower() in answer
	quiz['index'] = quiz['index'] + 1
	if(result):
		quiz['correct'] = quiz['correct'] + 1	
	return (quiz, result)

def is_quiz_over(quiz):
	return quiz['index'] >= len(quiz['questions'])	

#Use regexp to extract the search phrase
def extract_search_keyword(search_phrase):
	regexp = re.compile("(quiz|test) me on (\w+)")
	matches = regexp.match(search_phrase)
	return matches.group(2)

def generate_start(search_keyword):
	keyword = extract_search_keyword(search_keyword)
	quiz = parser.authorize(keyword)
	print(quiz)
	json_obj = {}
	json_obj["version"] = "1.0"
	resp = {'outputSpeech':{'type':'PlainText','text':'Lets begin. '+quiz['quiz']['questions'][0]['question']}}
	json_obj['sessionAttributes'] = quiz 
	resp['shouldEndSession'] = False 
	json_obj['response'] = resp
	return jsonify(json_obj)

#This will extract the user answer from the request
def get_user_answer():
	return request.get_json()['request']['intent']['slots']['QuestionAnswer']['value']

#produce a result string depending if the answer was correct or not
def parse_result(result):
	if(result):
		return "That was correct."
	else:
		quiz = get_current_quiz()
		return "That was incorrect. The answer is "+quiz['questions'][quiz['index']-1]['answer']

#Get the final score as a string
def get_final_score():
	quiz = get_current_quiz()
	total_questions = len(quiz['questions'])
	correct = quiz['correct']
	return str(correct)+" out of "+str(total_questions)+"."

def end_quiz():
	json_obj = {}
	json_obj["version"] = "1.0"
	resp = {'outputSpeech':{'type':'PlainText','text':'Game over. Your final score is '+get_final_score()}}
	resp['shouldEndSession'] = True
	json_obj['response'] = resp
	return jsonify(json_obj)

#Get the next question
def next_question():
	quiz = get_current_quiz()
	answer = get_user_answer()
	quiz,result = check_if_correct(quiz, answer)
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

#If there is an error, repeat a question
def repeat_question():
	quiz = get_current_quiz()
	json_obj = {}
	json_obj["version"] = "1.0"
	resp = {'outputSpeech':{'type':'PlainText','text':'I misunderstood. Here is the question again. '+quiz['questions'][quiz['index']]['question']}}
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
		search_value = request.get_json()['request']['intent']['slots']['QuestionType']['value']
		return generate_start(search_value)
	elif(is_answer()):
		try:
			return next_question()
		except:
			return repeat_question()
	else:
		return end_quiz()

app.run(host='0.0.0.0',port="443",debug=False,ssl_context=('cert.pem','key.pem'))
