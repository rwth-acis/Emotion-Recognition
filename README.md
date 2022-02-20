# Emotion-Recognition
A REST api which performs on request Speech and Text emotion recognition. Works together with a Mongo DB where the data is stored for future retrieval.
Is uses a known Github repository to train and evaluate a model which performs speech recognition. The training is done on various public datasets such as: 
- Ravdess
- EmoDB 
- TESS

<h1 align="center"><Emotion Recognition API></h1>

<p align="center"><This is a REST api which on requests performs Speech and Text emotion recognition. It works together with Mongo DB to store and retrieve emotional data.></p>

## Links

- [Github repo: Emotion Recognition Model and System](https://github.com/x4nth055/emotion-recognition-using-speech "Speech Emotion Recognition System")



<!-- ## Screenshots

![Home Page](/screenshots/1.png "Home Page")
cd ..
![](/screenshots/2.png)

![](/screenshots/3.png)  -->

## Available Functions

The Service expects RESTFUL Get and Post requests, a futher overview if possible by looking at the SWAGGER documentation:




### `static/emotion/speech" : "POST"`

```
POST <service-address>/static/emotion/speech
```

The application expects a JSON file with the audio file in base64 format in with the tag "fileBody", aswell as a a user identifier under the tag "userid", in order to properly store the entries on the database.
The response is JSON file with the predicted emotion, and speech to text result.

### `"static/emotion/text": "POST"`
```
POST <service-address>/static/emotion/text
```

The application expects a JSON file with the text under the tag "text", and a user identifier under the tag "userid".
The response is a JSON file with the predicted emotion. 

### `"/static/test/": "POST"`
```
POST <service-address>/static/test
```

A connection test. It expects a JSON file, the respond should be the same JSON file



## Database

To be a able to collect the data for later use, this webservice need to pare with an instance of a MongoDB. Then, after each recollection or recognition an entry will be stored in the data base Emotion/Users with the predicted text, predicted emotion, and an identifier. 