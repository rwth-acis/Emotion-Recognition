import configparser
import argparse


#Variables, this are the fundamental ones
# LANGUAGE (language for the speech to text engine)
# MONGO_HOST
# MONGO_PORT
# RASA_URL
# PORT (for the flask app)




parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, help="Language for the speech to text engine")
parser.add_argument("--mongodb", help="MongoDB's server address")
parser.add_argument("--p", help="Port for this application")
args = parser.parse_args()

config = configparser.ConfigParser()
config["DEFAULT"] = {"LANGUAGE": args.lang, "MONGO_PORT": args.mongodb,
"PORT":args.p}

f = open("config.ini", mode="w", encoding="utf-8")
config.write(f)
f.flush()
f.close()

