from travel_mapper.agent.Agent import Agent
from travel_mapper.routing.RouteFinder import RouteFinder
from dotenv import load_dotenv
from pathlib import Path
import os


def load_secets():
    load_dotenv()
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)

    open_ai_key = os.getenv("OPENAI_API_KEY")
    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")

    return {"OPENAI_API_KEY": open_ai_key, "GOOGLE_MAPS_API_KEY": google_maps_key}


def assert_secrets(secrets_dict):
    assert secrets_dict["OPENAI_API_KEY"] is not None
    assert secrets_dict["GOOGLE_MAPS_API_KEY"] is not None


class TravelMapper(object):
    def __init__(self, openai_api_key, google_maps_key, verbose=False):
        self.travel_agent = Agent(open_ai_api_key=openai_api_key, debug=verbose)
        self.route_finder = RouteFinder(google_maps_api_key=google_maps_key)

    def parse(self, query, make_map=True):
        itinerary, list_of_places = self.travel_agent.suggest_travel(query)

        directions, sampled_route, mapping_dict = self.route_finder.generate_route(
            list_of_places=list_of_places, itinerary=itinerary, include_map=make_map
        )
