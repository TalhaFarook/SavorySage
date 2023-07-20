from flask import Flask, render_template
from flask import request

import pandas
import random
import numpy
import re

import spacy
nlp = spacy.load("en_core_web_sm")
SSModel = spacy.load('SavorySage')

from sklearn.metrics.pairwise import cosine_similarity
from geopy.geocoders import Nominatim

location, cuisine, budget, rating = '', '', '', ''

app = Flask(__name__)


@app.route('/process_input', methods=['POST'])

def process_input():

    input_data = request.json['input']
    latitude = request.json['latitude']
    longitude = request.json['longitude']
    coordCheck = request.json['coordCheck']

    response = generate_response(input_data, latitude, longitude, coordCheck)

    return response


@app.route('/')

def home():

    return render_template('index.html')

def generate_response(input_data, latitude, longitude, coordCheck):

    response = createResponse(input_data, latitude, longitude, coordCheck)
    return response

def createResponse(query, latitude, longitude, coordCheck):

    data = pandas.read_csv('cleanedData.csv')

    location, cuisine, budget, rating = '', '', '', ''

    if coordCheck == 0:
        location, cuisine, budget, rating = extractEntitiesWithoutLocation(query)

        response = ''
        if not location or not cuisine or not budget or not rating:
            response = 'Can you please provide me your'

            if not location:
                response += ' location,'
            if not cuisine:
                response += ' cuisine,'
            if not budget:
                response += ' budget,'
            if not rating:
                response += ' rating,'

            response += ' so I can give you better suggestions!'
            response += ' ' + random.choice(['😃', '😄', '😁', '😇', '🤗'])

            return response
    
    elif coordCheck == 1:
        cuisine, budget, rating = extractEntitiesWithLocation(query)

        response = ''
        if not cuisine or not budget or not rating:
            response = 'Can you please tell me your'

            if not cuisine:
                response += ' cuisine of choice,'
            if not budget:
                response += ' budget,'
            if not rating:
                response += ' rating,'

            response += ' so I can give you better suggestions!'
            response += ' ' + random.choice(['😃', '😄', '😁', '😇', '🤗'])
        
            return response 
    
    filteredRestaurants = data[
        data['main_cuisine'].str.contains(cuisine)
    ]

    weights = numpy.array([1, 1, 0.7, 0.5])
    latitude, longitude = extractCoordinates(location)

    inputFilteredRestaurants = filteredRestaurants[['latitude', 'longitude', 'budget', 'rating']] * weights
    inputUserChoice = [[latitude, longitude, budget, rating]] * weights

    similarityScores = cosine_similarity(inputUserChoice, inputFilteredRestaurants)[0]

    recommendedRestaurants = filteredRestaurants.iloc[similarityScores.argsort()[::-1]]
    topRecommendedRestaurants = recommendedRestaurants.head(3)

    response, counter = f"Here are some recommendations for <b>{cuisine.capitalize()}</b> cuisine generated by my algorithm:<br>", 1
    for index, restaurant in topRecommendedRestaurants.iterrows():
        address = extractAddress(restaurant['latitude'], restaurant['longitude'])
        response += f"<br>{counter})  <b>{restaurant['name']}</b> is a great option. It has a rating of <b>{restaurant['rating']}</b> and a total of <b>{restaurant['review_number']}</b> reviews!<br>The address is <b>{address}</b>.<br>"
        counter += 1
        
    return response

def extractEntitiesWithoutLocation(query):

    global location, cuisine, budget, rating

    if location and cuisine and budget and rating:
        location, cuisine, budget, rating = '', '', '', ''

    doc = SSModel(query)

    for ent in doc.ents:
        if ent.label_ == 'CUISINE' and not cuisine:
            cuisine = ent.text.lower()
        elif ent.label_ == 'RATING' and not rating:
            rating = float(ent.text)
        elif ent.label_ == 'PK_CITY' and not location:
            location = ent.text.lower()
        elif ent.label_ == 'MONEY' and not budget:
            money = int(ent.text)
            if money <= 700:
                budget = 1
            elif money > 700 and money < 1300:
                budget = 2
            else:
                budget = 3
        elif ent.label_ == 'PK_CURRENCY':
            match = re.search(r'\d+', ent.text)
            if match:
                money = int(match.group())
                if money <= 700:
                    budget = 1
                elif money > 700 and money < 1300:
                    budget = 2
                else:
                    budget = 3
    
    return location, cuisine, budget, rating

def extractEntitiesWithLocation(query):

    global cuisine, budget, rating

    if cuisine and budget and rating:
        cuisine, budget, rating = '', '', ''

    doc = SSModel(query)

    for ent in doc.ents:
        if ent.label_ == 'CUISINE' and not cuisine:
            cuisine = ent.text.lower()
        elif ent.label_ == 'RATING' and not rating:
            rating = float(ent.text)
        elif ent.label_ == 'MONEY' and not budget:
            money = int(ent.text)
            if money <= 700:
                budget = 1
            elif money > 700 and money < 1300:
                budget = 2
            else:
                budget = 3
        elif ent.label_ == 'PK_CURRENCY':
            match = re.search(r'\d+', ent.text)
            if match:
                money = int(match.group())
                if money <= 700:
                    budget = 1
                elif money > 700 and money < 1300:
                    budget = 2
                else:
                    budget = 3

    return cuisine, budget, rating

def extractCoordinates(city):

    geolocator = Nominatim(user_agent="resturantChatbot")
    location = geolocator.geocode(city)
    
    latitude = location.latitude
    longitude = location.longitude

    return latitude, longitude

def extractAddress(latitude, longitude):
    
    geolocator = Nominatim(user_agent="resturantChatbot")
    geolocator.headers['Accept-Language'] = 'en'
    location = geolocator.reverse(f"{latitude}, {longitude}")
        
    return location.address

if __name__ == '__main__':
    app.run(debug=True)