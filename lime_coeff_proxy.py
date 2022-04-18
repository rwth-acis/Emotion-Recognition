
from pickle import GLOBAL
from flask import Flask, Response, request
import requests
import json
from uuid import uuid4
import ast
import base64
import pymongo
# import copy
# import configparser
from apscheduler.schedulers.background import BackgroundScheduler
# import time
import atexit




MONGO_HOST =  "localhost" #"137.226.232.75"
MONGO_PORT =  27017 #32112
#URL_2 = "https://affibot.limesurvey.net/index.php/admin/remotecontrol"
#API_USER_2 = "juanstuecker"
#API_PASSWORD_2 = "5rqimdSdwR6E"
#SURVEY_ID_2 = 589811
#SURVEY_ID_3 = 113484
SURVEY_IDS = {244663:"Metabolic Integration",375586: "Protein Metabolism"}


URL = "https://limesurvey.tech4comp.dbis.rwth-aachen.de/index.php/admin/remotecontrol"
API_USER = "stuecker"
API_PASSWORD = "janhw3QS4Wrr"
SURVEY_ID = 294243
HEADERS = {'content-type': 'application/json'}

NUM_QUESTIONS = 3
PORT = 5000 


#todo: create function to get participants list directly from the LRS, or the Mentoring Cockpit Service
participants = [
    {"email": "luisalanger@gmail.com", "firstname": "luisa"},
    {"email": "juan.stuecker@rwth-aachen.de", "firstname": "juan"},
    {"email": "danielastuckermtz@gmail.com", "firstname": "dany"}]



def set_params(method, params):
    data = {'method': method, 'params': params, 'id': str(uuid4())}
    return json.dumps(data)

def get_session_key():

    params = {'username': API_USER, 'password': API_PASSWORD}
    data = set_params('get_session_key', params)
    print(data)
    request = requests.post(URL, data=data, headers=HEADERS)
    return request.json()['result']
def extract_data(sessionKey: str, surveyID:int, documentType:str):
    params = {"sSessionKey": sessionKey, "iSurveyID": surveyID, "sDocumentType": documentType}
    data = set_params("export_responses", params)
    print(data)
    request = requests.post(URL, data= data, headers=HEADERS)
    return request.json()
def list_participants(sessionKey, survey_id, start=0, limit=1000, unused=False,
            attributes=False, conditions=[]):
    params = {"sSessionKey": sessionKey, "iSurveyID": survey_id, "iStart":start, "iLimit":limit, "bUnused": unused,"aAttributes":attributes, "aConditions":conditions}
    data = set_params('list_participants', params)
    print(data)
    request = requests.post(URL, data=data, headers=HEADERS)
    return request.json()
def list_questions(sessionKey, survey_id):
    params = {"sSessionKey": sessionKey, "iSurveyID": survey_id}
    data = set_params('list_questions', params)
    print(data)
    request = requests.post(URL, data=data, headers=HEADERS)
    return request.json()
def get_survey_coeffs2(surveyid:int):

    try:
        survey_data = extract_data(sessionKey= get_session_key(), surveyID= surveyid, documentType= "json")
        survey_data_decoded = base64.b64decode(survey_data["result"])
        json_data = json.loads(survey_data_decoded.decode("utf-8"))
        responses_dict = {}
        for i in json_data["responses"]:
            for j in i: 
                #token of each response
                token = i[j]["token"]
                responses_dict[token] = []
                for k in range(NUM_QUESTIONS):
                    responses_dict[token].append(["Q"+str(k+1)+"[SQ001]",i[j]["Q"+str(k+1)+"[SQ001]"]])
                    
        return responses_dict
    except Exception as ex:
        print(ex)
def get_participants_token(survey_id):
    participants = list_participants(get_session_key(), survey_id)
    user_token = {}
    for i in participants["result"]:
        user_token[i["token"]] = i["participant_info"]["email"]
    return user_token

def get_item_valence(dict, item_name):
    # i1= [0,1,2]
    # i2 = [3,4,5]
    student_item = {}

    for i in dict:
        valence = []
        student_item[i] = {}
        for j in range(NUM_QUESTIONS):
            valence.append(0)
            # if j in i1:
            if dict[i][j][1] != '' and dict[i][j][1] :
                valence[0] += int(dict[i][j][1])
                # student_item[i]["Item 1"] = valence
            # elif j in i2:
            #     if dict[i][j][1] != '' :
            #         valence[1] += int(dict[i][j][1])
        
        student_item[i][item_name] = valence[0]
        # student_item[i]["2"] = valence[1]
    return student_item

def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]

APP = Flask(__name__)

@APP.route("/get_link", methods = ["POST"])
def get_link(): 
    global SURVEY_IDS
    try: 

        json_data = request.get_json(force = True)
        email = json_data["email"]
        quiz_urls = []

        # survey_id = json_data["surveyid"]
        for i in SURVEY_IDS: 
            print("Going through quiz"+ str(i))

        
            token = get_keys_from_value(get_participants_token(survey_id=i),email)
            if (len(token)>1):
                print("WARNING:There is more than one token linked with this email!")
                for j in token: 
                    quiz_urls.append("https://limesurvey.tech4comp.dbis.rwth-aachen.de/index.php/"+str(i)+"?token="+str(j)+"&lang=en")
                
                    
            else: 
                print("There is just one account linked to this email "+ str(len(token))+str(type(token)))
                quiz_urls.append("https://limesurvey.tech4comp.dbis.rwth-aachen.de/index.php/"+str(i)+"?token="+str(token[0])+"&lang=en")
        return str(quiz_urls)
    except Exception as ex: 
        print("Error sending quiz link")
        print(ex)


@APP.route("/test_routine", methods = ["POST"])
def test_routine(): 
    print("Triggered routine!")
    return ""

@APP.route("/start_routine", methods = ["POST"])
def start_routine(): 
    #this phew lines do the whole trick! 
    global SURVEY_IDS
    
    update_list = []

    for i in SURVEY_IDS: 
        dict =get_survey_coeffs2(i)
        participants_tokens = get_participants_token(i)
        items = get_item_valence(dict, SURVEY_IDS[i])
        for j in items:
            if j in participants_tokens:
                for k in items[j]:
                    update_list.append({"userid":participants_tokens[j],"item":str(k), "valence":items[j][k] })
    global LIST 
    LIST = update_list
    if update_list: 
        try:
            db_response = db_quizes.users.insert_many(update_list)
        except Exception as ex: 
            print("Something went wrong creating the responses")
            print(ex)

    return "Success"


@APP.route("/trigger_routine", methods = ["POST"])
def trigger_routine(): 
    #this phew lines do the whole trick! 
    for i in SURVEY_IDS: 
        dict =get_survey_coeffs2(i)
        participants_tokens = get_participants_token(i)
        items = get_item_valence(dict, SURVEY_IDS[i])
        update_list = []
        for j in items:
            if j in participants_tokens:
                for k in items[j]:
                    update_list.append({"userid":participants_tokens[j],"item":str(k), "valence":items[j][k] })
    global LIST
    updated_elements = [i for i in LIST if i not in update_list]
    # new_elements= [i for i in update_list if i not in LIST] actually, this way around is not needed at all
    if updated_elements: 
        try:
            db_response = db_quizes.users.insert_many(updated_elements)
        except Exception as ex: 
            print("Somthing went wrong updating the responses")
            print(ex)

    return "Success"

"""
    At this point the updated list contains all scores for the items in the limesurvey
"""

LIST = []
UPDATED_LIST = []


try: 
    print("Trying to connect with the database...")
    mongo = pymongo.MongoClient(
         host=MONGO_HOST,  
         port= MONGO_PORT, 
         serverSelectionTimeoutMS = 10000
         )
    print("Checking connection with the DB")
    mongo.server_info()  #triggers the exception if no connection
    db = mongo.course
    db_quizes = mongo.quizes
    print("SUCCESS: connecting with the DB!")

except Exception as ex:    
    print("ERROR: Cannot connect to the databse") 
    print(ex)
else: 
    start_routine()


scheduler = BackgroundScheduler()
scheduler.add_job(func = trigger_routine, trigger="interval", seconds = 10000)
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    scheduler.start()
    APP.run(host = '0.0.0.0', port = PORT, debug = True)
    atexit.register(lambda: scheduler.shutdown())



