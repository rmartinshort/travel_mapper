from travel_mapper.agent.Agent import Agent
from travel_mapper.routing.RouteFinder import RouteFinder
from dotenv import load_dotenv
from pathlib import Path
import os


def test(query=None):
    load_dotenv()
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)

    open_ai_key = os.getenv("OPENAI_API_KEY")
    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not query:
        query = """
        I want to do 3 week trip from Berkeley CA to New York City.
        I want to visit national parks and cities with good food.
        I want use a rental car and drive for no more than 3 hours on any given day. 
        """

    # set up agent
    travel_agent = Agent(open_ai_api_key=open_ai_key, debug=False)
    # set up route calculator, which contains the mapper
    route_finder = RouteFinder(google_maps_api_key=google_maps_key)

    itinerary, list_of_places = travel_agent.suggest_travel(query)
    directions, sampled_route, mapping_dict = route_finder.generate_route(
        list_of_places=list_of_places, itinerary=itinerary, include_map=True
    )
