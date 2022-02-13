from deep_emotion_recognition import DeepEmotionRecognizer
from flask import Flask, Response, request
#import pymongo
import json
#from bson.objectid import ObjectId
import datetime
import base64
import os
import sys
#from bson.json_util import dumps
#from utils import get_best_estimators
import pyaudio
import speech_recognition as sr
from flask_swagger_ui import get_swaggerui_blueprint
from pydub import AudioSegment
import logging


def handle_audio(json_data): 
# this function should detect the type of audio file the request sent, and decode it correctly from base64 into a PL wav format.
    name = json_data["fileName"]
    audio_64 = json_data["fileBody"]
    fileType = name[-3:]
    if  fileType == "mp3":
        try: 
            mp3_file_temp = open("temp.mp3", "wb")
            audio_decoded = base64.b64decode(audio_64)
            mp3_file_temp.write(audio_decoded)
            # APP.logger.info("The final object type is: " + str(type(mp3_file_temp)))
            # APP.logger.info("Until here everything should be good!! and the base 64 should be decoded into something")
            filename_mp3 = "temp.mp3"
            filename_wav = "newtemp.wav"

            # converting mp3 to wav
            src = filename_mp3
            dst = filename_wav
            sound = AudioSegment.from_mp3(src)
            sound.export(dst, format = "wav")
            # APP.logger.info("Correctly changed format from MP3 to WAV!, approaching next step")
            # APP.logger.info(filename_wav)

        except Exception as ex: 
            pass
            #APP.logger.info("Could not convert filetype " + file_type+ " to .wav")

    if fileType == "m4a": 
        try: 
            m4a_file_temp = open("temp.m4a", "wb")
            audio_decoded = base64.b64decode(audio_64)
            m4a_file_temp.write(audio_decoded)
            # APP.logger.info("The final object type is: " + str(type(mp3_file_temp)))
            # APP.logger.info("Until here everything should be good!! and the base 64 should be decoded into something")
            filename_m4a = "temp.m4a"
            filename_wav = "newtemp.wav"

            # converting mp3 to wav
            src = filename_m4a
            dst = filename_wav
            sound = AudioSegment.from_file(filename_m4a, format = "m4a")
            sound.export(dst, format = "wav")
            # APP.logger.info("Correctly changed format from MP3 to WAV!, approaching next step")
            # APP.logger.info(filename_wav)

            

        except Exception as ex:
            print(ex) 

    return filename_wav

# logger_emo = logging.getLogger("deep_emotion_recognition")
# logger_emo.setLevel(logging.CRITICAL)
# logger_emo.propagate = False

#logging.getLogger("APP").setLevel(logging.INFO)






LANGUAGE = "en"
MONGO_HOST = "localhost"
MONGO_PORT = 27017

APP = Flask(__name__)
recognizer = sr.Recognizer()


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


try: 
    APP.logger.info("Training the model")
    deepemo = DeepEmotionRecognizer(emotions=['angry', 'sad', 'neutral', 'ps', 'happy'], n_rnn_layers=2, n_dense_layers=2, rnn_units=128, dense_units=128, verbose = False)
    deepemo.train()
    print("Test accuracy score: {:.3f}%".format(deepemo.test_score()*100))
except Exception as ex: 
    APP.logger.info(ex)
# detector = EmotionRecognizer(emotions=["sad", "neutral","happy", "angry", "bored"], verbose=0)
# detector.train()
# print("Test accuracy score: {:.3f}%".format(detector.test_score()*100))



#SWAGGER initialization
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

#speech emotion recognition training


# print(os.getcwd())
# def get_estimators_name(estimators):
#     result = [ '"{}"'.format(estimator.__class__.__name__) for estimator, _, _ in estimators ]
#     return ','.join(result), {estimator_name.strip('"'): estimator for estimator_name, (estimator, _, _) in zip(result, estimators)}

# estimators = get_best_estimators(True)
# estimators_str, estimator_dict = get_estimators_name(estimators)
# features = ["mfcc", "chroma", "mel"]
# detector = EmotionRecognizer(estimator_dict["BaggingClassifier"], emotions=["sad", "neutral","happy", "ps", "angry"], features=features, verbose=0)
# detector.train()
# print("Test accuracy score: {:.3f}%".format(detector.test_score()*100))




#Connecting with the database# WIll have to comment that in once it works with kube
# try: 
#     print("Trying to connect with the database...")
#     mongo = pymongo.MongoClient(
#          host=MONGO_HOST, 
#          port= MONGO_PORT, 
#          serverSelectionTimeoutMS = 10000
#          )
#     print("Checking connection with the server")
#     mongo.server_info()  #triggers the exception if no connection
#     print("Until now, everything is good")
#     db = mongo.course
#     db_emotion = mongo.emotion
#     print("SUCCESS: connecting with the DB!")

# except Exception as ex:    
#     print("ERROR: Cannot connect to the databse") 
#     print(ex)


#given noSQL is not a relatinoal data-base system, there is really no need in initializing the users with an APPropiate /user function, instead the only methods avaliable will be /emotion/speech, and /emotion/text
# this function should detect the type of audio file the request sent, and decode it correctly from base64 into a PL wav format.

@APP.route("/static/emotion/speech/", methods = ["POST"])

def speech_emotion_recognition(): 

    try: 
        APP.logger.info("Extracting JSON data")
        try:
            json_data = request.get_json(force = True) #output is of type DICT
        #     data_type = json_data["fileName"]
        #     audio = json_data["fileBody"]
        #     #course_id = json_data["course_id"]
        #     #item_id = json_data["item_id"] #optional parameter 
        #     user_id = json_data["user"]
        #     time = datetime.datetime.now()
        except Exception as ex: 
        #     APP.logger.info("Something went wrong extracting JSON data")
            print(ex)    



        # #TODO: Implement audio_handling function to spare this code
        # APP.logger.info("The type fo the audio file extracted from the jason data is"+ str(type(audio)))
        # APP.logger.info("Creating a temporary mp3 file, the file will be stored in:")
        # APP.logger.info(str(os.getcwd()))
        # mp3_file = open("temp.mp3", "wb")
        # APP.logger.info("Decoding base64...")
        # decode_string = base64.b64decode(audio)
        # mp3_file.write(decode_string)
        # APP.logger.info("The final object type is: " + str(type(mp3_file)))
        # APP.logger.info("Until here everything should be good!! and the base 64 should be decoded into something")
        # filename = "temp.mp3"
        # filename_wav = "newtemp.wav"

        # # converting mp3 to wav
        # src = filename
        # dst = filename_wav
        # sound = AudioSegment.from_mp3(src)
        # sound.export(dst, format = "wav")
        # APP.logger.info("Correctly changed format from MP3 to WAV!, approaching next step")
        # APP.logger.info(filename_wav)

        filename_wav = handle_audio(json_data)
        text_result = ""

        try: 
            with sr.AudioFile(filename_wav) as source: 
                audio_data = recognizer.record(source)
                text_result = recognizer.recognize_google(audio_data, language = LANGUAGE)
                APP.logger.info("****************The SPEECH TO TEXT result is ************")
                APP.logger.info(text_result)
        except Exception as ex:
            APP.logger.info(ex)
            APP.logger.info("Something went wrong trying to perform speech to text")
            APP.logger.info(ex) 



        

        # recognizing emotion
        try: 
            emotion_array = deepemo.predict_proba(filename_wav)

        except Exception as ex:
            APP.logger.info(ex)
     

        update = {#"user_id": user_id, 
        # "course_id":course_id,
        #  "item_id": item_id,
        #   "audio_type": data_type,
        #    "emotion": ["predicted", 
        #    "emotion",
        #     "activation",
        #      "coeffs"],
        #       "valence": 1,
        #        "time": "today",
                "text": (text_result + "| predicted_emotion:" + str(emotion_array))
                }

        # dbResponse = db_emotion.users.insert_one(update) MONGODB
        # print(dbResponse.inserted_id) MONGODB




        return json.dumps(update)
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
        print(ex) 


@APP.route("/static/emotion/speech/<fileName>/", methods = ["DELETE"])
def detele_audio_file(fileName): 
    try: 
        if os.path.exists(str(fileName)+".wav"):
            print("Trying to remove the file "+ str(fileName)+ " now")
            os.remove(fileName+".wav")
            return "SUCESS: file deteled"
        else: 
            print("The file does not exist in the directory" )  

    except Exception as ex: 
        print("Could not remove the file becasue :")
        print(ex)




@APP.route("/static/emotion/text/", methods = ["POST"])
def text_emotion_recognition():
    return "text works"


#MONGODB
# @APP.route("static/emotion/<user>/<item>/", methods = ["GET"])

# def get_emotion_data(user, item): 
#     try: 

#         query = db_emotion.users.find( {"user_id": user, "item_id":item} )
#         print("Before being converted the query was of type: "+str(type(query)))
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
#         print("Coould not query data: ")
#         print(ex)    

@APP.route("/static/test/", methods = ["POST"])
def test_json(): 
    print("TESTING JSON DATA EXTRACTION")
    APP.logger.info("This is the app logger")
    try:
        json_data = request.get_json(force = True) #output is of type DICT
        if (request.data): 
            print("Data size is: "+ str(len(request.data)))
            print("Data type is: "+ str(type(request.data)))
        # if (json_data): 
        #     print("THERE IS JSON DATA IN THE REQUEST")
        #     print("of type: "+ str(type(json_data)))    
        for attr in request.args: 
            print(attr)
        return json.dumps(json_data)

    except Exception as ex: 
        print("Could not extract JSON file")
        APP.logger.info(ex)
        APP.logger.info("Could not perform the function")
        print(ex)











if __name__ == "__main__":
    APP.run(host = '0.0.0.0', port = 5002, debug = True)

