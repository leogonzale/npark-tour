from flask import Flask, render_template, request
import logging
from datetime import datetime
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.output_parsers import JsonOutputParser
import json

# Initialize the OpenAI language model
llm = OpenAI(
   max_tokens = -1 # not recommended!!
)

# Initialize the output parser
parser = JsonOutputParser()

# app will run at: http://127.0.0.1:5000/

# Initialize logging
logging.basicConfig(filename="app.log", level=logging.INFO)
log = logging.getLogger("app")

# Initialize the Flask application
app = Flask(__name__)

# Create a prompt to build a new trip
def build_new_trip_prompt_template():
    examples = [
        {
          "prompt":
"""
This trip is to Yosemite National Park between 2024-05-23 and 2024-05-25. This person will be traveling solo, with kids and would like to stay in campsites. They want to go hiking, swimming. Create a daily itinerary for this trip using this information. You are a backend data processor that is part of our site's programmatic workflow. Output the itinerary as only JSON with no text before or after the JSON.
""",
          "response": """{{"trip_name":"My awesome trip to Yosemite 2024 woohoooo","location":"Yosemite National Park","trip_start":"2024-05-23","trip_end":"2024-05-25","traveling_with":"solo, with kids","lodging":"campsites","adventure":"hiking, swimming","itinerary":[{{"day":"1","date":"2024-05-23","morning":"Arrive at Yosemite National Park","afternoon":"Set up campsite at North Pines Campground","evening":"Explore the campground and have a family campfire dinner"}},{{"day":"2","date":"2024-05-24","morning":"Guided tour of Yosemite Valley (includes stops at El Capitan, Bridalveil Fall, Half Dome)","afternoon":"Picnic lunch in the Valley","evening":"Relax at the campsite, storytelling around the campfire"}},{{"day":"3","date":"2024-05-25","morning":"Hike to Mirror Lake (easy hike, great for kids)","afternoon":"Swimming at Mirror Lake","evening":"Dinner at the campsite, stargazing"}}]}}"""
        },
                {
          "prompt":
"""
This trip is to Yosemite National Park between 2024-05-23 and 2024-05-25. This person will be traveling solo, with kids and would like to stay in campsites. They want to go hiking, swimming. Create a daily itinerary for this trip using this information. You are a backend data processor that is part of our site's programmatic workflow. Output the itinerary as only JSON with no text before or after the JSON.
""",
          "response": """{{"trip_name":"My awesome trip to Yosemite 2024 woohoooo","location":"Yosemite National Park","trip_start":"2024-05-23","trip_end":"2024-05-25","traveling_with":"solo, with kids","lodging":"campsites","adventure":"hiking, swimming","itinerary":[{{"day":"1","date":"2024-05-23","morning":"Arrive at Yosemite National Park","afternoon":"Set up campsite at North Pines Campground","evening":"Explore the campground and have a family campfire dinner"}},{{"day":"2","date":"2024-05-24","morning":"Guided tour of Yosemite Valley (includes stops at El Capitan, Bridalveil Fall, Half Dome)","afternoon":"Picnic lunch in the Valley","evening":"Relax at the campsite, storytelling around the campfire"}},{{"day":"3","date":"2024-05-25","morning":"Hike to Mirror Lake (easy hike, great for kids)","afternoon":"Swimming at Mirror Lake","evening":"Dinner at the campsite, stargazing"}}]}}"""
        }
    ]

    example_prompt = PromptTemplate.from_template(
      template =
"""
{prompt}\n{response}
"""
    )

    few_shot_prompt = FewShotPromptTemplate(
      examples = examples,
      example_prompt = example_prompt,
      suffix = "This trip is to {location} between {trip_start} and {trip_end}. This person will be traveling {traveling_with} and would like to stay in {lodging}. They want to {adventure}. Create an daily itinerary for this trip using this information. You are a backend data processor that is part of our site's programmatic workflow. Output the itinerary as only JSON with no text before or after the JSON.",
      input_variables = ["location", "trip_start", "trip_end", "traveling_with", "lodging", "adventure"],
    )

    return few_shot_prompt

# Create a prompt for the typical weather conditions
def build_weather_prompt_template():
    examples = [
      {
        "prompt":
"""
Update the following JSON object to include typical weather conditions for the trip based on the values of trip_start, trip_end, and location. Keep the object exactly as it is, and add a key / value pair to the JSON, with the key being typical_weather and the value being a string describing the typical weather for the time period. Add this key / value pair after the key / value pair with a key of location. You are a backend data processor that is part of our site's programmatic workflow. Output the updated itinerary as only JSON with no text before or after the JSON.
{{"trip_name":"Family Bird-Watching Trip to Acadia 2024","location":"Acadia National Park","trip_start":"2024-08-07","trip_end":"2024-08-10","traveling_with":"kids","lodging":"bed & breakfasts","adventure":"bird-watching","itinerary":[{{"day":"1","date":"2024-08-07","morning":"Arrive at Acadia National Park","afternoon":"Check in at bed & breakfast","evening":"Relax and explore the property"}},{{"day":"2","date":"2024-08-08","morning":"Bird-watching excursion at Jordan Pond","afternoon":"Picnic lunch at Jordan Pond House","evening":"Dinner at a local seafood restaurant"}},{{"day":"3","date":"2024-08-09","morning":"Explore the Schoodic Peninsula","afternoon":"Hike the Schoodic Head Trail","evening":"Dinner and stargazing at the bed & breakfast"}},{{"day":"4","date":"2024-08-10","morning":"Bird-watching cruise around Frenchman Bay","afternoon":"Visit the Wild Gardens of Acadia","evening":"Farewell dinner in Bar Harbor"}}]}}
""",
        "response":
"""
{{"trip_name":"Family Bird-Watching Trip to Acadia 2024","location":"Acadia National Park","typical_weather":"In August, the weather in Acadia National Park is typically warm with daytime highs around 75 degrees F (24 degrees C) and cool evenings, along with occasional rain showers.","trip_start":"2024-08-07","trip_end":"2024-08-10","traveling_with":"kids","lodging":"bed & breakfasts","adventure":"bird-watching","itinerary":[{{"day":"1","date":"2024-08-07","morning":"Arrive at Acadia National Park","afternoon":"Check in at bed & breakfast","evening":"Relax and explore the property"}},{{"day":"2","date":"2024-08-08","morning":"Bird-watching excursion at Jordan Pond","afternoon":"Picnic lunch at Jordan Pond House","evening":"Dinner at a local seafood restaurant"}},{{"day":"3","date":"2024-08-09","morning":"Explore the Schoodic Peninsula","afternoon":"Hike the Schoodic Head Trail","evening":"Dinner and stargazing at the bed & breakfast"}},{{"day":"4","date":"2024-08-10","morning":"Bird-watching cruise around Frenchman Bay","afternoon":"Visit the Wild Gardens of Acadia","evening":"Farewell dinner in Bar Harbor"}}]}}
"""
      },
{
        "prompt":
"""
Update the following JSON object to include typical weather conditions for the trip based on the values of trip_start, trip_end, and location. Keep the object exactly as it is, and add a key / value pair to the JSON, with the key being typical_weather and the value being a string describing the typical weather for the time period. Add this key / value pair after the key / value pair with a key of location. You are a backend data processor that is part of our site's programmatic workflow. Output the itinerary as only JSON with no text before or after the JSON.
{{"trip_name": "Solo trip to Kenai Fjords 2024 yay!", "location": "Kenai Fjords National Park", "trip_start": "2024-12-01", "trip_end": "2024-12-03", "traveling_with": "solo", "lodging": "lodges", "adventure": "hiking, guided tours", "itinerary": [{{"day": "1", "date": "2024-12-01", "morning": "Arrive at Kenai Fjords National Park", "afternoon": "Check into lodge", "evening": "Relax and explore surrounding area"}}, {{"day": "2", "date": "2024-12-02", "morning": "Guided hike to Exit Glacier", "afternoon": "Lunch at the lodge", "evening": "Sunset cruise through the Kenai Fjords"}}, {{"day": "3", "date": "2024-12-03", "morning": "Morning kayak excursion", "afternoon": "Guided tour of Harding Icefield", "evening": "Farewell dinner at the lodge"}}]}}
""",
        "response":
"""
{{"trip_name": "Solo trip to Kenai Fjords 2024 yay!", "location": "Kenai Fjords National Park","typical_weather":"In December, the weather in Kenai Fjords National Park is typically cold with temperatures often below freezing and frequent precipitation, including snow and rain.","trip_start": "2024-12-01", "trip_end": "2024-12-03", "traveling_with": "solo", "lodging": "lodges", "adventure": "hiking, guided tours", "itinerary": [{{"day": "1", "date": "2024-12-01", "morning": "Arrive at Kenai Fjords National Park", "afternoon": "Check into lodge", "evening": "Relax and explore surrounding area"}}, {{"day": "2", "date": "2024-12-02", "morning": "Guided hike to Exit Glacier", "afternoon": "Lunch at the lodge", "evening": "Sunset cruise through the Kenai Fjords"}}, {{"day": "3", "date": "2024-12-03", "morning": "Morning kayak excursion", "afternoon": "Guided tour of Harding Icefield", "evening": "Farewell dinner at the lodge"}}]}}
"""
      }
    ]

    example_prompt = PromptTemplate.from_template(
      template =
"""
{prompt}\n{response}
"""
    )

    few_shot_prompt = FewShotPromptTemplate(
      examples = examples,
      example_prompt = example_prompt,
      suffix = "Update the following JSON object to include typical weather conditions for the trip based on the values of trip_start, trip_end, and location. Keep the object exactly as it is, and add a key / value pair to the JSON, with the key being typical_weather and the value being a string describing the typical weather for the time period. Add this key / value pair after the key / value pair with a key of location. You are a backend data processor that is part of our site's programmatic workflow. Output the itinerary as only JSON with no text before or after the JSON. {input}",
      input_variables = ["input"],
    )
    return few_shot_prompt

# Define the route for the home page
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
  
# Define the route for the plan trip page
@app.route("/plan_trip", methods=["GET"])
def plan_trip():
  return render_template("plan-trip.html")

# Define the route for view trip page with the generated trip itinerary
@app.route("/view_trip", methods=["POST"])
def view_trip():
  traveling_with_list = ", ".join(request.form.getlist("traveling-with"))
  lodging_list = ", ".join(request.form.getlist("lodging"))
  adventure_list = ", ".join(request.form.getlist("adventure"))

  prompt = build_new_trip_prompt_template()

  chain = prompt | llm | parser

  output = chain.invoke({
    "location": request.form["location-search"],
    "trip_start": request.form["trip-start"],
    "trip_end": request.form["trip-end"],
    "traveling_with": traveling_with_list,
    "lodging": lodging_list,
    "adventure": adventure_list,
    "trip_name": request.form["trip-name"]
  })
  
  log.info(output)

  prompt2 = build_weather_prompt_template()
  
  chain2 = prompt2 | llm | parser

  output_str = json.dumps(output)

  output2 = chain2.invoke({"input": output_str})
  
  log.info(output2)

  return render_template("view-trip.html", output = output2)

    
# Run the flask server
if __name__ == "__main__":
    app.run()