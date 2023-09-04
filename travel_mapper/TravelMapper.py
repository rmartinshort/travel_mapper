from travel_mapper.agent.Agent import Agent
import leafmap.foliumap as leafmap
import folium
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
        """
        For running when we don't want to call gradio
        """
        itinerary, list_of_places, validation = self.travel_agent.suggest_travel(query)

        directions, sampled_route, mapping_dict = self.route_finder.generate_route(
            list_of_places=list_of_places, itinerary=itinerary, include_map=make_map
        )

    def generate_without_leafmap(self, query, model_name):
        # set the model name to call
        self.travel_agent.chat_model.model_name = model_name
        itinerary, list_of_places, validation = self.travel_agent.suggest_travel(query)

        if validation["validation_output"].dict()["updated_request"]:
            validation_body = validation["validation_output"].dict()["updated_request"]
            validation_header = "The query is not valid in its curret state. Here is a suggestion from the model: \n"
            validation = validation_header + validation_body
            return None, validation
        else:
            validation = "Plan is valid"

        return itinerary, validation

    def generate_with_leafmap(self, query, model_name):

        # set the model name to call
        self.travel_agent.chat_model.model_name = model_name
        itinerary, list_of_places, validation = self.travel_agent.suggest_travel(query)

        if validation["validation_output"].dict()["updated_request"]:
            validation_body = validation["validation_output"].dict()["updated_request"]
            validation_header = "The query is not valid in its curret state. Here is a suggestion from the model: \n"
            validation = validation_header + validation_body
            # need to be able to set a blank HTML, or just a generic map here
            return "", None, validation
        else:
            validation = "Plan is valid"

        directions_list, sampled_route, mapping_dict = self.route_finder.generate_route(
            list_of_places=list_of_places, itinerary=itinerary, include_map=False
        )

        map_start_loc_lat = directions_list[0]["legs"][0]["start_location"]["lat"]
        map_start_loc_lon = directions_list[0]["legs"][0]["start_location"]["lng"]
        map_start_loc = [map_start_loc_lat, map_start_loc_lon]

        marker_points = []

        # extract the location points from the previous directions function
        for segment in directions_list:
            for leg in segment["legs"]:
                leg_start_loc = leg["start_location"]
                marker_points.append(
                    ([leg_start_loc["lat"], leg_start_loc["lng"]], leg["start_address"])
                )

        last_stop = directions_list[-1]["legs"][-1]
        last_stop_coords = last_stop["end_location"]
        marker_points.append(
            (
                [last_stop_coords["lat"], last_stop_coords["lng"]],
                last_stop["end_address"],
            )
        )

        map = leafmap.Map(location=map_start_loc, tiles="Stamen Terrain", zoom_start=8)

        # Add waypoint markers to the map
        for location, address in marker_points:
            folium.Marker(
                location=location,
                popup=address,
                tooltip="<strong>Click for address</strong>",
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(map)

        for leg_id, route_points in sampled_route.items():
            leg_distance = route_points["distance"]
            leg_duration = route_points["duration"]

            f_group = folium.FeatureGroup("Leg {}".format(leg_id))
            folium.vector_layers.PolyLine(
                route_points["route"],
                popup="<b>Route segment {}</b>".format(leg_id),
                tooltip="Distance: {}, Duration: {}".format(leg_distance, leg_duration),
                color="blue",
                weight=2,
            ).add_to(f_group)
            f_group.add_to(map)

        return map.to_gradio(), itinerary, validation
