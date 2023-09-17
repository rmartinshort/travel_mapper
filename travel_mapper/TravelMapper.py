from travel_mapper.agent.Agent import Agent
from travel_mapper.routing.RouteFinder import RouteFinder
from travel_mapper.user_interface.utils import (
    generate_leafmap,
    validation_message,
    generate_generic_leafmap,
)
from dotenv import load_dotenv
from pathlib import Path
from travel_mapper.user_interface.constants import VALID_MESSAGE
import os


def load_secrets():
    load_dotenv()
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)

    open_ai_key = os.getenv("OPENAI_API_KEY")
    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
    google_palm_key = os.getenv("GOOGLE_PALM_API_KEY")

    return {
        "OPENAI_API_KEY": open_ai_key,
        "GOOGLE_MAPS_API_KEY": google_maps_key,
        "GOOGLE_PALM_API_KEY": google_palm_key,
    }


def assert_secrets(secrets_dict):
    assert secrets_dict["OPENAI_API_KEY"] is not None
    assert secrets_dict["GOOGLE_MAPS_API_KEY"] is not None
    assert secrets_dict["GOOGLE_PALM_API_KEY"] is not None


class TravelMapperBase(object):
    def __init__(
        self, openai_api_key, google_palm_api_key, google_maps_key, verbose=False
    ):
        self.travel_agent = Agent(
            open_ai_api_key=openai_api_key,
            google_palm_api_key=google_palm_api_key,
            debug=verbose,
        )
        self.route_finder = RouteFinder(google_maps_api_key=google_maps_key)

    def parse(self, query, make_map=True):
        """
        For running when we don't want to call gradio
        """
        itinerary, list_of_places, validation = self.travel_agent.suggest_travel(query)

        directions, sampled_route, mapping_dict = self.route_finder.generate_route(
            list_of_places=list_of_places, itinerary=itinerary, include_map=make_map
        )


class TravelMapperForUI(TravelMapperBase):
    def _model_type_switch(self, new_model_name):
        """

        Parameters
        ----------
        new_model_name

        Returns
        -------

        """
        current_model_name = self.travel_agent.chat_model.model_name
        if ("gpt" in current_model_name and "gpt" not in new_model_name) or (
            "bison" in current_model_name and "bison" not in new_model_name
        ):
            # change the model family
            self.travel_agent.update_model_family(new_model_name)
        elif current_model_name != new_model_name:
            self.travel_agent.chat_model.model_name = new_model_name

    def generate_without_leafmap(self, query, model_name):
        """

        Parameters
        ----------
        query
        model_name

        Returns
        -------

        """
        self._model_type_switch(model_name)

        itinerary, list_of_places, validation = self.travel_agent.suggest_travel(query)

        # make validation message
        validation_string = validation_message(validation)

        if validation_string != VALID_MESSAGE:
            itinerary = "No valid itinerary"

        return itinerary, validation_string

    def generate_with_leafmap(self, query, model_name):
        """

        Parameters
        ----------
        query
        model_name

        Returns
        -------

        """
        self._model_type_switch(model_name)

        itinerary, list_of_places, validation = self.travel_agent.suggest_travel(query)

        # make validation message
        validation_string = validation_message(validation)

        if validation_string != VALID_MESSAGE:
            itinerary = "No valid itinerary"
            # make a generic map here
            map_html = generate_generic_leafmap()

        else:
            (
                directions_list,
                sampled_route,
                mapping_dict,
            ) = self.route_finder.generate_route(
                list_of_places=list_of_places, itinerary=itinerary, include_map=False
            )

            map_html = generate_leafmap(directions_list, sampled_route)

        return map_html, itinerary, validation_string
