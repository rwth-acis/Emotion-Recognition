from deep_emotion_recognition import DeepEmotionRecognizer
from flask import Flask, Response, request
import pymongo
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
# global variables referenced in the functions
# filename_wav = ""
# filename_mp3 = ""
# emotion_array = ""
# text_result = ""

LANGUAGE = "en-US" #for the speech to text engine
MONGO_HOST = "137.226.232.75"
MONGO_PORT = 32112


APP = Flask(__name__)

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

def handle_audio(json_data): 
# this function should detect the type of audio file the request sent, and decode it correctly from base64 into a PL wav format.
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
            APP.logger.info("Until now no problem")


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
            APP.logger.info("Error with filetype: mp3")

    if (fileType == "m4a"): 
        try: 

            audio_decoded = base64.b64decode(audio_64)

            filename = "temp.m4a"
            filename_export = "wavtemp.wav"

            file_temp = open(filename, "wb")
            file_temp.write(audio_decoded)
            APP.logger.info("Until now no problem")

            # converting m4a to wav
            src = filename
            dst = filename_export
            try: 
                sound = AudioSegment.from_file(src, format ="m4a")
                sound = sound.split_to_mono()[0]
                APP.logger.info("SUCESS: audio decoding")
            except: 
                sound = AudioSegment.from_file(src, format = "mp4")
                APP.logger.info("Changed to mp4 format")    
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

#Changing log level for the emotion recognition module
# logger_emo = logging.getLogger("deep_emotion_recognition")
# logger_emo.setLevel(logging.CRITICAL)
# logger_emo.propagate = False

#Change the log level of this app
#logging.getLogger("APP").setLevel(logging.INFO)



#Speech to text recognizer
recognizer = sr.Recognizer()

#Changin log configuration to show logs from flask
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



#Connection to the Databse
try: 
    APP.logger.info("Trying to connect with the database...")
    mongo = pymongo.MongoClient(
         host=MONGO_HOST, 
         port= MONGO_PORT, 
         serverSelectionTimeoutMS = 10000
         )
    APP.logger.info("Checking connection with the server")
    mongo.server_info()  #triggers the exception if no connection
    db = mongo.course
    db_emotion = mongo.emotion
    APP.logger.info("SUCCESS: connecting with the DB!")

except Exception as ex:    
    APP.logger.info("ERROR: Cannot connect to the databse") 
    APP.logger.info(ex)


#given noSQL is not a relatinoal data-base system, there is really no need in initializing the users with an APPropiate /user function, instead the only methods avaliable will be /emotion/speech, and /emotion/text
# this function should detect the type of audio file the request sent, and decode it correctly from base64 into a PL wav format.

@APP.route("/static/emotion/speech/", methods = ["POST"])

def speech_emotion_recognition(): 

    try: 
        APP.logger.info("Extracting JSON data")
        try:
            json_data = request.get_json(force = True) #output is of type DICT
        #     data_type = json_data["fileName"]
        #     #course_id = json_data["course_id"]
        #     #item_id = json_data["item_id"] #optional parameter 
            user_mail = json_data["email"]
            time = datetime.datetime.now()
      
        except Exception as ex: 
        #     APP.logger.info("Something went wrong extracting JSON data")
            APP.logger.info(ex)    



        # #TODO: Implement audio_handling function to spare this code --- 
        # OLD code to transform base 64 -> audio -> wav, not with function handle_audio(json)
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
        # speech to text
        text_result = "Not found"
        try: 
            with sr.AudioFile(filename_wav) as source: 
                audio_data = recognizer.record(source)
                text_result = recognizer.recognize_sphinx(audio_data, language = LANGUAGE)
                APP.logger.info("****************The SPEECH TO TEXT result is *******************")
                APP.logger.info(text_result)
        except Exception as ex:
            APP.logger.info(ex)
            APP.logger.info("Something went wrong trying to perform speech to text")



        
        emotion_array = ""
        # recognizing emotion
        try: 
            emotion_array = deepemo.predict_proba(filename_wav)
            APP.logger.info("Predicted emotion succesfully")

        except Exception as ex:
            APP.logger.info(ex)


        try: 
            if os.path.exists(str(filename_wav)):
                APP.logger.info("Attemting to remove file "+ str(filename_wav)+ " now")
                os.remove(filename_wav)
                APP.logger.info("SUCCESS, temp file deleted")
            else: 
                APP.logger.info("The file does not exist in the directory" )  

        except Exception as ex: 
            APP.logger.info("Could not remove the file becasue :")
            APP.logger.info(ex)    

            


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
        update_db = {"user_id": user_mail, 
        # "course_id":course_id,
        #  "item_id": item_id,
        #   "audio_type": data_type,
        #    "emotion": ["predicted", 
        #    "emotion",
        #     "activation",
        #      "coeffs"],
        #       "valence": 1,
                "time": time,
                "text": text_result, 
                "emotion": str(emotion_array)

                }        

        dbResponse = db_emotion.users.insert_one(update_db) 
        APP.logger.info("Database insertion succesfull!" + str(dbResponse.inserted_id)) 




        return json.dumps(update_bot)
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
    return "This function is still not implemented in this version of the service, but will be in the future"


#MONGODB query handler for the emotion from a user for a specif item
@APP.route("/static/emotion/<user>/<item>/", methods = ["GET"])

def get_emotion_data(user, item): 
    try: 

        query = db_emotion.users.find( {"user_id": user, "item_id":item} )
        APP.logger.info("Before being converted the query was of type: "+str(type(query)))
        query_list = list(query)[0] # this is of type DICT, so searching should be easy
        query_json = {"Emotion": query_list["emotion"], "Valence": query_list["valence"]
        }

        #return json.dumps(query_json)

        return Response(
        response = json.dumps(query_json), 
        status = 200, 
        mimetype = "application/json"
        )
    except Exception as ex: 
        APP.logger.info("Coould not query data: ")
        APP.logger.info(ex)    





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


@APP.route("/static/getLowest", methods = ["GET"])
def getLowest(): 
    #todo: incorporate the k to get the lowest k values, right now the method returns all matching documents
    try:
        json_data = request.get_json(force = True) #output is of type DICT
        if (request.data): 
            user = json_data["user"]
            num = json_data["numberOfElements"]
        try: 

            #this queries any document of the user, where the valence is greater than 0,  meaning, all documents where there is an entry on valence of emotion.
            query = db_emotion.users.find( { "user_id": user, "valence": { "$gte": 0 } } )


            query_list = list(query) # this is of type DICT, so searching should be easy

            query_json = {}

            for i in range(len(query_list)): 
                query_json["document" + str(i)] = str(query_list[i])

            return Response(
            response = json.dumps(query_json), 
            status = 200, 
            mimetype = "application/json"
            )
        except Exception as ex: 
            APP.logger.info("Coould not query data: ")
            APP.logger.info(ex)    
        









    except Exception as ex:
        print(ex)














if __name__ == "__main__":
    APP.run(host = '0.0.0.0', port = 5002, debug = True)

