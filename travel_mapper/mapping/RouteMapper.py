from datetime import datetime
import folium
from branca.element import Figure
from travel_mapper.constants import MAPS_DUMP_DIR
import logging
import os

logging.basicConfig(level=logging.INFO)


class RouteMapper:
    def __init__(self, h=500, w=1000):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.figure = Figure(height=h, width=w)
        self.map_name = "route_map.html"
        self.save_map = True
        self.map = None

    def add_list_of_places(self, list_of_places):
        """

        Parameters
        ----------
        list_of_places

        Returns
        -------

        """
        self.map_name = self.auto_generate_map_name(list_of_places)

    def auto_generate_map_name(self, list_of_places):
        """

        Parameters
        ----------
        list_of_places

        Returns
        -------

        """
        return "{}_{}_{}_trip.html".format(
            str(datetime.today().date()).replace("-", "_"),
            list_of_places["start"].split(",")[0].replace(" ", "_"),
            list_of_places["end"].split(",")[0].replace(" ", "_"),
        )

    def generate_and_display(self, directions_list, route_dict):
        """

        Parameters
        ----------
        directions_list
        route_dict

        Returns
        -------

        """
        map = self.generate_route_map(self, directions_list, route_dict)
        self.figure.add_child(map)

    def generate_route_map(self, directions_list, route_dict):
        """

        Parameters
        ----------
        directions_list
        route_dict

        Returns
        -------

        """
        map_start_loc_lat = directions_list[0]["legs"][0]["start_location"]["lat"]
        map_start_loc_lon = directions_list[0]["legs"][0]["start_location"]["lng"]
        map_start_loc = [map_start_loc_lat, map_start_loc_lon]

        marker_points = []

        # extract the location points from the previous directions function
        self.logger.info("Generating marker_points for map")
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

        self.logger.info("Setting up the map")

        map = folium.Map(location=map_start_loc, tiles="OpenStreetMap", zoom_start=10)

        # Add waypoint markers to the map
        for location, address in marker_points:
            folium.Marker(
                location=location,
                popup=address,
                tooltip="<strong>Click for address</strong>",
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(map)

        # Add lines to the map

        self.logger.info("Adding route segments to the map")

        for leg_id, route_points in route_dict.items():
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

        if self.save_map:
            self.logger.info("Saving map to {}/{}".format(MAPS_DUMP_DIR, self.map_name))
            if not os.path.isdir(MAPS_DUMP_DIR):
                self.logger.info("Generating maps dir {}".format(MAPS_DUMP_DIR))
                os.mkdir(MAPS_DUMP_DIR)
            map.save(os.path.join(MAPS_DUMP_DIR, self.map_name))

        self.map = map
