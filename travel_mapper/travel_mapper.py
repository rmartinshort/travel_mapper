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
        I want to do a 30 day trip from Cape Town to Windhoek.
        I want to see some national parks and desert landscapes.
        I don't want to drive more than 3 hours per day.
        """

    travel_agent = Agent(open_ai_api_key=open_ai_key, debug=False)
    route_finder = RouteFinder(google_maps_api_key=google_maps_key)

    itinerary, list_of_places = travel_agent.suggest_travel(query)
    directions, sampled_route, mapping_dict = route_finder.generate_route(
        list_of_places=list_of_places, itinerary=itinerary, include_map=True
    )
