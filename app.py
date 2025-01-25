from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.output_parsers import JsonOutputParser



#llm = OpenAI()


llm = OpenAI(
    max_tokens = -1
)
 
parser = JsonOutputParser()
# app will run at: http://127.0.0.1:5000/

# Initialize logging
logging.basicConfig(filename="app.log", level=logging.INFO)
log = logging.getLogger("app")

# Initialize the Flask application
app = Flask(__name__)

	
def build_new_trip_prompt(form_data):
  examples = [
   {  
      "prompt":
"""
This trip is to Yosemite National Park between 2024-05-23 and 2024-05-25. 
This person will be traveling solo, with kids and would like to stay in campsites. 
They want to hiking, swimming. Create a daily itinerary for this trip using this information.  You are a backend data processor that is part of our site's programmatic workflow. Output the itinerary as only JSON with no text before or after the JSON.
""",
      "response":
 
"""
{{"trip_name":"My awesome trip to Yosemite 2024 woohoooo","location":"Yosemite National Park","trip_start":"2024-05-23","trip_end":"2024-05-25","num_days":"3","traveling_with":"solo, with kids","lodging":"campsites","adventure":"hiking, swimming","itinerary":[{{"day":"1","date":"2024-05-23","morning":"Arrive at Yosemite National Park","afternoon":"Set up campsite at North Pines Campground","evening":"Explore the campground and have a family campfire dinner"}},{{"day":"2","date":"2024-05-24","morning":"Guided tour of Yosemite Valley (includes stops at El Capitan, Bridalveil Fall, Half Dome)","afternoon":"Picnic lunch in the Valley","evening":"Relax at the campsite, storytelling around the campfire"}},{{"day":"3","date":"2024-05-25","morning":"Hike to Mirror Lake (easy hike, great for kids)","afternoon":"Swimming at Mirror Lake","evening":"Dinner at the campsite, stargazing"}}]}}
"""
 
   },
   {  
      "prompt": 
"""This trip is to Yosemite National Park from 2024-05-23 to 2024-05-25. 
person travels solo, with kids and prefer to stay in campsites. 
They want to hiking, swimming. Create a daily itinerary for this trip using this information. You are a backend data processor that is part of our site's programmatic workflow. Output the itinerary as only JSON with no text before or after the JSON.""",
      "response":  """{{"trip_name": "Zion Here I Come}}"""
   },

  ]

  example_prompt = PromptTemplate.from_template(
    template =
"""
{prompt}\n{response}
"""
  )
  
  # log.info(example_prompt.format(**examples[0]))
  
  few_shot_prompt = FewShotPromptTemplate(
    examples = examples,
    example_prompt = example_prompt,
    suffix = "{input}",
    input_variables = ["input"],
  )

  return few_shot_prompt.format(input = "This trip is to " + form_data["location"] + " between " + form_data["trip_start"] + " and "
   +  form_data["trip_end"] + ". This person will be traveling " + form_data["traveling_with_list"] + " and would like to stay in " + form_data["lodging_list"]
    + ". They want to " + form_data["adventure_list"] + ". Create an daily itinerary for this trip using this information. You are a backend data processor that is part of our app’s programmatic workflow. Output the itinerary as only JSON with no text before or after the JSON.")


  
  '''
   prompt_template = PromptTemplate.from_template("This trip is to {location} between {trip_start} and {trip_end}. This person will be traveling {traveling_with_list} and would like to stay in {lodging_list}. They want to {adventure_list}. Create a daily itinerary for this trip using this information.")
                                                  
   return prompt_template.format(
        location = form_data["location"],
        trip_start = form_data["trip_start"],
        trip_end = form_data["trip_end"],
        traveling_with_list = form_data["traveling_with_list"],
        lodging_list = form_data["lodging_list"],
        adventure_list = form_data["adventure_list"]
    )
    '''
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
  #log.info(request.form)
  traveling_with_list = ",".join(request.form.getlist("traveling-with"))
  lodging_list = ", ".join(request.form.getlist("lodging"))
  adventure_list = ", ".join(request.form.getlist("adventure"))
 

  cleaned_form_data = {
        "location": request.form["location-search"],
        "trip_start": request.form["trip-start"],
        "trip_end": request.form["trip-end"],
        "traveling_with_list": traveling_with_list,
        "lodging_list": lodging_list,
        "adventure_list": adventure_list,
        "trip_name": request.form["trip-name"]
    }

  prompt = build_new_trip_prompt(cleaned_form_data)

  log.info(prompt)
  
  response = llm.invoke(prompt)
  #log.info(response)
  output = parser.parse(response)

  log.info(output)

  '''
  log.info(prompt)
  return render_template("view-trip.html")
  '''
  #return render_template("view-trip.html")

  return render_template("view-trip.html", output = output)

# Run the flask server
if __name__ == "__main__":
    app.run()
