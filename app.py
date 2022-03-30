from deep_emotion_recognition import DeepEmotionRecognizer
from emotion_recognition import EmotionRecognizer
from flask import Flask, Response, request
import pymongo
import json
import datetime
import base64
import os
import sys
from bson.json_util import dumps
import speech_recognition as sr
from flask_swagger_ui import get_swaggerui_blueprint
from pydub import AudioSegment
import logging
import numpy
import requests
import configparser

#todo: make all url, and changing variables to env variables on startup

# LANGUAGE = "en-US" #for the speech to text engine
# MONGO_HOST = "localhost"#"137.226.232.75" #"localhost"
# MONGO_PORT = 27017#32112 # 27017
# RASA_URL =  "http://localhost:5005/model/parse" #"http://rasa-nlu.ba-stuecker:5005/model/parse" #"http://localhost:5005/model/parse" #
# RASA_URL_2 = "http://rasa-nlu.svc.cluster.local:5005/model/parse"
# RASA_URL_3 = "http//rasa_nlu:5005/model/parse"
# PORT = 50022
try:
    print("Config: Getting config information from config.ini")
    config = configparser.ConfigParser()
    config.read("config.ini")

    LANGUAGE = config.get("KUBE", "LANGUAGE")
    MONGO_HOST = config.get("KUBE", "MONGO_HOST")
    MONGO_PORT = config.get("KUBE", "MONGO_PORT")
    RASA_URL = config.get("KUBE","RASA")
    PORT = config.get("KUBE","PORT")
    print("Config: Success extracting the variables from the config file!")
except Exception as ex:
    print("Config: Something went wrong extracting the variables fromt he config file")
    print(ex)
else: 
    LANGUAGE = LANGUAGE
    MONGO_HOST = MONGO_HOST
    MONGO_PORT = MONGO_PORT
    RASA_URL = RASA_URL
    PORT = PORT
    

EMOTIONS = ["angry", "sad", "happy"]
LEARNIN_MODEL = "standard"
try: 
    if("happy" in os.environ["EMOTIONS"] ):
        print("EMOTIONS defined by user: "+ os.environ["EMOTIONS"])
        EMOTIONS = os.environ["EMOTIONS"]
    if (os.environ["LEARNING_MODEL"]):
        print("Learning model defined by user")
        LEARNING_MODEL = os.environ["LEARNING_MODEL"]
    else: 
        pass
except Exception as ex: 
    print(ex)


APP = Flask(__name__)

"""
    Swagger initialization

    Makes  url/swagger and url/static/swagger.json avaliable in order for the service to be detectable by the Social Bot Manager service

"""
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Speech and Text emotion recognition and processing API"
    }
)
APP.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

def handle_audio(json_data): 
    """
    Audio Handling

    Args:
        json_data  (json): a json string, contains an audio file in base64 format

    Returns:
        temp.wav (wav audio file): exports the decoded data into wav audio format in the file temp.wav

    """

    name = json_data["fileName"]
    audio_64 = json_data["fileBody"]
    fileType = name[-3:]
    if  fileType == "mp3":
        try: 

            audio_decoded = base64.b64decode(audio_64)

            filename = "temp.mp3"
            filename_export = "wavtemp.wav"

            file_temp = open(filename, "wb")
            file_temp.write(audio_decoded)


            # converting mp3 to wav
            src = filename
            dst = filename_export
            sound = AudioSegment.from_mp3(filename)
            sound = sound.split_to_mono()[0]
            # try: 
            #     sound = AudioSegment.from_file(src, format ="mp3")
            #     sound = sound.split_to_mono()[0]
            #     APP.logger.info("SUCESS: audio decoding")
            # except: 
            #     APP.logger.info("Attempting with mp4")
            #     sound = AudioSegment.from_file(src, format = "mp4")
            #     APP.logger.info("Changed to mp4 format")
            sound.export(dst, format = "wav")


        except Exception as ex: 
            APP.logger.info(ex)
            APP.logger.info("Audio Decoding: Error with filetype: mp3")
        else: 
            fileType = fileType

    if (fileType == "m4a"): 
        try: 

            audio_decoded = base64.b64decode(audio_64)

            filename = "temp.m4a"
            filename_export = "wavtemp.wav"

            file_temp = open(filename, "wb")
            file_temp.write(audio_decoded)

            # converting m4a to wav
            src = filename
            dst = filename_export
            try: 
                sound = AudioSegment.from_file(src, format ="m4a")
                sound = sound.split_to_mono()[0]
                APP.logger.info("Audio decoding: success")
            except: 
                sound = AudioSegment.from_file(src, format = "mp4")
                APP.logger.info("Audio decoding: Changed to mp4 format")    
            sound.export(dst, format = "wav")
            


        except Exception as ex:
            APP.logger.info(ex)
            APP.logger.info("m4a")

    if (fileType == "aac"): 
        try: 

            audio_decoded = base64.b64decode(audio_64)

            filename = "temp.aac"
            filename_export = "wavtemp.wav"

            file_temp = open(filename, "wb")
            file_temp.write(audio_decoded)
            APP.logger.info("Until now no problem")

            # converting aac to wav
            src = filename
            dst = filename_export
            try: 
                sound = AudioSegment.from_file(src, format ="aac")
                sound = sound.split_to_mono()[0]
                APP.logger.info("SUCESS: audio decoding")
            except: 
                sound = AudioSegment.from_file(src, format = "aac")
                APP.logger.info("Changed to mp4 format")    
            sound.export(dst, format = "wav")
            


        except Exception as ex:
            APP.logger.info(ex)
            APP.logger.info("aac")            
 

    return filename_export

def e_valence(e_array):
    """
    Args: 
        activation array with 5 emotions

    Returns: 
        Coefficient result of the product of the cross product with some weights which are adjustable

    """

    weights = [-0.5,-1,2,1]
    valence = numpy.dot(weights, list(e_array.values()))
    return valence

def get_intent(text:str):

    params = {'text': text}
    try:
        APP.logger.info("NLU: Attempting intention detection with rasa endpoint: "+ RASA_URL)
        request = requests.post(RASA_URL, json.dumps(params))
    except:
        APP.logger.info("NLU:Error, intention detection could not be performed")
    else: 
        return request.json()["intent"]["name"]


"""
    Speech to text fc.
        methods: 
            audio_data = reconizer.record(audio_file) preprocesses the data to be used by the model
            recognizer.reconizer_sphinx() makes prediction based on the CMX sphinx speech to text engine, alternatives can be found on their documentation

"""
recognizer = sr.Recognizer()

"""
    Configuration of Logs for the flask app:
        Can be changed by adjusting the logger.setLevel function to a number of different levels. This app has not configure any level other than INFO

"""
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


try: 
    """
        deepemo (DeepEmotionRecognizer) emotion prediction model, takes an array of possible emotions as arguments, and is trained with  .train() method.

        detector (EmotionReconizer) alternative model using classification models such as SVC, takes and array of possible emotions as arguments, and is trained with .train()

    """
    # APP.logger.info("Training the model")
    deepemo = DeepEmotionRecognizer(emotions=EMOTIONS, n_rnn_layers=2, n_dense_layers=2, rnn_units=128, dense_units=128, verbose = True)
    deepemo.train()
    print("Test accuracy score: {:.3f}%".format(deepemo.test_score()*100))

    #Alternative recognizer, uses classification methods instead of FNNs
    # deepemo = EmotionRecognizer(emotions=["sad","happy", "angry"], verbose=0)
    # deepemo.train()
    # print("Test accuracy score: {:.3f}%".format(deepemo.test_score()*100))

except Exception as ex: 
    APP.logger.info(ex)



try: 
    APP.logger.info("Database: Attempting connection")
    mongo = pymongo.MongoClient(
         host=MONGO_HOST, 
         port= int(MONGO_PORT), 
         serverSelectionTimeoutMS = 10000
         )
    APP.logger.info("Checking connection with the DB: "+ MONGO_HOST+":"+ MONGO_PORT)
    mongo.server_info() 
    db = mongo.course
    db_emotion = mongo.emotion
    db_quizes = mongo.quizes
    APP.logger.info("Database: Success in connecting!")

except Exception as ex:    
    APP.logger.info("Database: Error, could not connect") 
    APP.logger.info(ex)





"""
    Speech Emotion Recognition Function

    Args: Json file (string) containing: 
        user_mail: user email used to identify the user, this should match the email in the course registered in the Mentoring Cockpit service
        fileName: name of the audio file with correct extention: either .mp3, .mp4, .aac
        fileBody: base64 String of the audio coded
    Response: 
        JSON file contaning speech to text, emotion prediction, intent prediction, and metadata
"""
@APP.route("/static/emotion/speech/", methods = ["POST"])

def speech_emotion_recognition(): 

    try: 
        APP.logger.info("Json: Extracting JSON data")
        # Extracting variables from JSON
        try:
            json_data = request.get_json(force = True) #output is of type DICT
        #     data_type = json_data["fileName"]
        #    course_id = json_data["course_id"]
        #     #item_id = json_data["item_id"] #optional parameter 
            user_mail = json_data["email"]
            time = datetime.datetime.now()
      
        except Exception as ex: 
            APP.logger.info(ex)    
        else: 
            user_mail = user_mail
            json_data = json_data

        # Decoding base64 audio string
        filename_wav = handle_audio(json_data)

        # Performing speech to text on the resulting audio file
        text_result = "Not found"
        try: 
            with sr.AudioFile(filename_wav) as source: 
                audio_data = recognizer.record(source)
                text_result = recognizer.recognize_sphinx(audio_data, language = LANGUAGE)
                APP.logger.info("Speech to text: Success, result: "+ text_result)
        except Exception as ex:
            APP.logger.info(ex)
            APP.logger.info("Speech to text: Error: Something went wrong trying performing speech to text")
        else: 
            text_result = text_result



        # Predicting emotion on the resulting audio file

        emotion_array = ""
        valence = -1
        try: 
            emotion_array = deepemo.predict_proba(filename_wav)

            # Debug: APP.logger.info(type(emotion_array))
            APP.logger.info("Emotion Recognition: Predicted emotion succesfully: "+ str(emotion_array))
            valence = e_valence(emotion_array)
            APP.logger.info("Emotion Recognition: Valence was calculated correctly: "+ str(valence))
            max_value = max(zip(emotion_array.values(), emotion_array.keys()))[1]
            print("Emotion: The maximal value of the emotion array : "+ max_value)

        except Exception as ex:
            APP.logger.info(ex)
        else: 
            emotion_array = emotion_array
            valence = valence
            max_value = max_value
        emotion_array["angry"] = emotion_array["angry"]-0.3
        # Removing temporary files
        try: 
            if os.path.exists(str(filename_wav)):
                APP.logger.info("Temp removal: attemting to remove file "+ str(filename_wav))
                os.remove(filename_wav)
                APP.logger.info("Temp removal: temp file deleted")
            else: 
                APP.logger.info("Error while trying to remove temp file: The file does not exist in the directory" )  

        except Exception as ex: 
            APP.logger.info("Could not remove the file becasue :")
            APP.logger.info(ex)    
        
        #Intention detection with Rasa

        APP.logger.info("NLU: Performing intent detection by rasa server")
        intent = "no intent found"
        intent = get_intent(text_result)
        APP.logger.info("NLU: Intent detected: "+ intent)

            
        """
            update_bot (dictionary) can be used to directy communication with the bot, there for the text: ____ format

            update_db (dictionary) is used to update the data in the Mongo Database
        """

        update_bot = {#"user_id": user_id, 
        # "course_id":course_id,
        #  "item_id": item_id,
        #   "audio_type": data_type,
        #    "emotion": ["predicted", 
        #    "emotion",
        #     "activation",
        #      "coeffs"],
        #       "valence": 1,
        #        "time": "today",
                "text": ("predicted text:" + text_result + " | predicted_emotion:" + str(emotion_array))
                }
        update_db = {"email": user_mail, 
        # "course_id":course_id,
        #  "item_id": item_id,
        #   "audio_type": data_type,
        #    "emotion": ["predicted", 
        #    "emotion",
        #     "activation",
        #      "coeffs"],
               "valence": valence,
               "numOfSuggestions": 2,
                "intent": str(intent),
                "text": text_result, 
                "emotion": str(emotion_array), 
                "max_emotion": max_value

                }        

        dbResponse = db_emotion.users.insert_one(update_db) 
        APP.logger.info("Database: Insertion succesfull!: ID" + str(dbResponse.inserted_id)) 



        """
            Response to the Mentoring Cockpit service, or any other service making the requests: 

            updata_db: 

                email (string): user email used to identify the student in the service
                valence (double): result of the get_valence function, number result of the cross product of the activation array from the emtoion detection and some adjustable weights.
                numOfSuggestions (int): number of suggestions asked by the user
                intent (string): intent result from the NLU
                text (string): speech to text result 
                emotion (string): activation array from the emotion recognition service


        """
        return dumps(update_db)
        # Response(
        #     response = json.dumps(update
        #         # {"message":"Emotion Stored","emotion :": "toDo",
        #         # #  "id":f"{dbResponse.inserted_id}",
        #         #   "user": user_id, "course": course_id, "text": text
        #         # }
        #     ), 
        #     status = 200, 
        #     mimetype = "application/json"
            
        #  )

    except Exception as ex:
        APP.logger.info(ex) 

# Previous version of a function to delete spefici files in the contaienr
# @APP.route("/static/emotion/speech/<fileName>/", methods = ["DELETE"])
# def detele_audio_file(fileName): 
#     try: 
#         if os.path.exists(str(fileName)+".wav"):
#             print("Trying to remove the file "+ str(fileName)+ " now")
#             os.remove(fileName+".wav")
#             return "SUCESS: file deteled"
#         else: 
#             print("The file does not exist in the directory" )  

#     except Exception as ex: 
#         print("Could not remove the file becasue :")
#         print(ex)



"""
    Text emotion recognition: 
    Args: 
        Text (string): Incoming text

    Result: 
        Emotion (string): Emotion predicted from the text
"""
@APP.route("/static/emotion/text/", methods = ["POST"])
def text_emotion_recognition():
    return "This function is still not implemented in this version of the service, but will be in the future"

#Previous version of  a function to get the valence from a specific user and an item
# @APP.route("/static/emotion/<user>/<item>/", methods = ["GET"])

# def get_emotion_data(user, item): 
#     try: 

#         query = db_emotion.users.find( {"user_id": user, "item_id":item} )
#         APP.logger.info("Before being converted the query was of type: "+str(type(query)))
#         query_list = list(query)[0] # this is of type DICT, so searching should be easy
#         query_json = {"Emotion": query_list["emotion"], "Valence": query_list["valence"]
#         }

#         #return json.dumps(query_json)

#         return Response(
#         response = json.dumps(query_json), 
#         status = 200, 
#         mimetype = "application/json"
#         )
#     except Exception as ex: 
#         APP.logger.info("Coould not query data: ")
#         APP.logger.info(ex)    




# Test function for incoming / outgoing stream of JSON data
# @APP.route("/static/test/", methods = ["POST"])
# def test_json(): 
#     print("TESTING JSON DATA EXTRACTION")
#     APP.logger.info("This is the app logger")
#     try:
#         json_data = request.get_json(force = True) #output is of type DICT
#         if (request.data): 
#             print("Data size is: "+ str(len(request.data)))
#             print("Data type is: "+ str(type(request.data)))
#         # if (json_data): 
#         #     print("THERE IS JSON DATA IN THE REQUEST")
#         #     print("of type: "+ str(type(json_data)))    
#         for attr in request.args: 
#             print(attr)
#         return json.dumps(json_data)

#     except Exception as ex: 
#         print("Could not extract JSON file")
#         APP.logger.info(ex)
#         APP.logger.info("Could not perform the function")
#         print(ex)

"""
    get K Lowest items

    Args: 
        json body (JSON): Json file as string containing following variables: 

            user (string): id of the user, usually email
            num (int): number of suggestions asked by the user, meaning number of items being requested for this function
            valence (double): valence of the user during the request
"""
@APP.route("/static/getLowest/", methods = ["POST"])
def getLowest(): 
    try:
        json_data = request.get_json(force = True) #output is of type DICT
        if (request.data): 
            try:
                user = json_data["email"]
                num = json_data["numOfSuggestions"]
                #courseid = json_data["courseid"]
                #todo: incorporate valence as a filter for the result
                #valence = json_data["valence"]
            except Exception as ex: 
                APP.logger.info("Lowest: Missing in JSON file for request")  
                APP.logger.info(ex)  
            else : 
                user = user 
                num = num
        try: 
            query = db_emotion.users.find( { "user_id": user, "valence": { "$gte": 0 } } ).sort("valence", -1).limit(int(num))
            
            query_list = list(query) # this is of type DICT, so searching should be easy
            APP.logger.info("Database: Query result frmo mongo: " + str(query_list))
            

            query_json = {}

            for i in range(len(query_list)): 
                query_json["ITEM number: " + str(i+1)] = str(query_list[i]["_id"])

            return Response(
            response = json.dumps(query_json), 
            status = 200, 
            mimetype = "application/json"
            )
        except Exception as ex: 
            APP.logger.info("LOWEST: Could not query data: ")
            APP.logger.info(ex)    

    except Exception as ex:
        print(ex)



if __name__ == "__main__":
    APP.run(host = '0.0.0.0', port = PORT, debug = True)

