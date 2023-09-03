from travel_mapper.mapping.RouteMapper import RouteMapper
from googlemaps.convert import decode_polyline
import googlemaps
from datetime import datetime
import numpy as np
import logging
import time

logging.basicConfig(level=logging.INFO)

class RouteFinder:
    MAX_WAYPOINTS_API_CALL = 23

    def __init__(self, google_maps_api_key):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.mapper = RouteMapper()
        self.gmaps = googlemaps.Client(key=google_maps_api_key)

    def generate_route(self, list_of_places, itinerary, include_map=True):
        self.logger.info("# " * 20)
        self.logger.info("PROPOSED ITINERARY")
        self.logger.info("# " * 20)
        self.logger.info(itinerary)

        t1 = time.time()
        directions, sampled_route, mapping_dict = self.build_route_segments(
            list_of_places
        )
        t2 = time.time()
        self.logger.info("Time to build route : {}".format((round(t2 - t1, 2))))

        if include_map:
            t1 = time.time()
            self.mapper.add_list_of_places(list_of_places)
            self.mapper.generate_route_map(directions, sampled_route)
            t2 = time.time()
            self.logger.info("Time to generate map : {}".format((round(t2 - t1, 2))))

        return directions, sampled_route, mapping_dict

    def build_route_segments(
        self, list_of_places, verbose=True, sample_route_points=5000
    ):
        number_of_stops = len(list_of_places["waypoints"])

        segment_mapping_dicts = []
        directions_list = []
        routes_list = []
        sampled_routes = []

        # if this is true, we need to make several API calls to collect the entire route
        if number_of_stops > self.MAX_WAYPOINTS_API_CALL:
            self.logger.info(
                "Number of stops ({}) > MAX_WAYPOINTS_PER_CALL ({}), going to make several calls to Google Maps API".format(
                    number_of_stops, self.MAX_WAYPOINTS_API_CALL
                )
            )
            starting_point = list_of_places["start"]
            segment_id = 0
            for segment_start in range(0, number_of_stops, self.MAX_WAYPOINTS_API_CALL):
                segment_end = segment_start + self.MAX_WAYPOINTS_API_CALL

                segment_waypoints = list_of_places["waypoints"][
                    segment_start:segment_end
                ]

                if segment_end >= number_of_stops:
                    # this is the final segment
                    end_point = list_of_places["end"]
                else:
                    end_point = segment_waypoints[-1]

                start_point = starting_point

                mapping_dict = self.build_mapping_dict(
                    start_point, end_point, waypoints=segment_waypoints[:-1]
                )

                if verbose:
                    self.logger.info("# " * 10)
                    self.logger.info(
                        "Getting directions for segment {}".format(segment_id)
                    )

                directions, route = self.build_directions_and_route(
                    mapping_dict, verbose=verbose
                )
                sampled_route = self.sample_route_with_legs(
                    route, npoints=sample_route_points
                )

                directions_list += directions
                routes_list += route
                sampled_routes.append(sampled_route)

                segment_mapping_dicts.append(mapping_dict)

                starting_point = end_point
                segment_id += 1

            # combine and assemble as single mapping dict and route list from the segments
            mapping_dict, sampled_route = self.assemble_final_route_from_segments(
                segment_mapping_dicts, sampled_routes
            )
            directions = directions_list

        # if we can just do one API call to Google Maps, then the process is simpler
        else:
            self.logger.info("Assembling mapping dictionary")
            mapping_dict = self.build_mapping_dict(
                list_of_places["start"],
                list_of_places["end"],
                waypoints=list_of_places["waypoints"],
            )

            self.logger.info("Calling Google Maps API to get directions")
            directions, route = self.build_directions_and_route(mapping_dict)
            sampled_route = self.sample_route_with_legs(
                route, npoints=sample_route_points
            )

        return directions, sampled_route, mapping_dict

    def convert_to_coords(self, input_address):
        return self.gmaps.geocode(input_address)

    def build_mapping_dict(self, start, end, waypoints):
        mapping_dict = {}
        mapping_dict["start"] = self.convert_to_coords(start)[0]
        mapping_dict["end"] = self.convert_to_coords(end)[0]

        if waypoints:
            for i, waypoint in enumerate(waypoints):
                mapping_dict["waypoint_{}".format(i)] = self.convert_to_coords(
                    waypoint
                )[0]

        return mapping_dict

    @staticmethod
    def get_route(directions_result):
        waypoints = {}

        for leg_number, leg in enumerate(directions_result[0]["legs"]):
            leg_route = {}

            distance = leg["distance"]["text"]
            duration = leg["duration"]["text"]
            leg_route["distance"] = distance
            leg_route["duration"] = duration
            leg_route_points = []

            for step in leg["steps"]:
                decoded_points = decode_polyline(step["polyline"]["points"])
                for p in decoded_points:
                    leg_route_points.append(f'{p["lat"]},{p["lng"]}')

            leg_route["route"] = leg_route_points
            waypoints[leg_number] = leg_route

        return waypoints

    def build_directions_and_route(
        self, mapping_dict, start_time=None, transit_type=None, verbose=True
    ):
        if not start_time:
            start_time = datetime.now()

        if not transit_type:
            transit_type = "driving"

        waypoints = [
            mapping_dict[x]["formatted_address"]
            for x in mapping_dict.keys()
            if "waypoint" in x
        ]
        start = mapping_dict["start"]["formatted_address"]
        end = mapping_dict["end"]["formatted_address"]

        directions_result = self.gmaps.directions(
            start,
            end,
            waypoints=waypoints,
            mode=transit_type,
            units="metric",
            optimize_waypoints=True,
            traffic_model="best_guess",
            departure_time=start_time,
        )

        if not directions_result:
            # if we get here, the google maps call has failed. This is probably because
            # the waypoints were not found. We can still make a map by just using the
            # start and end locations but we need to warn the user that the map won't contain
            # the waypoints

            self.logger.warning(
                "WARNING, some of the waypoints {} seem to"
                "have caused issues with the google maps api".format(waypoints)
            )

            self.logger.warning(
                "Directions will just be between start {} and end {}".format(start, end)
            )

            directions_result = self.gmaps.directions(
                start, end, units="metric", optimize_waypoints=True
            )

        if verbose:
            print("# " * 10)
            print("Fetched directions")
            print("# " * 10)
            # print out some stats for the legs of the proposed trip
            for i, leg in enumerate(directions_result[0]["legs"]):
                print(
                    "Stop:" + str(i),
                    leg["start_address"],
                    "==> ",
                    leg["end_address"],
                    "distance (km): ",
                    leg["distance"]["value"] / 1000,
                    "traveling Time (hrs): ",
                    leg["duration"]["value"] / 3600,
                )

        full_route = self.get_route(directions_result)

        return directions_result, full_route

    @staticmethod
    def assemble_final_route_from_segments(segment_mapping_dicts, sampled_routes):
        final_mapping_dict = {}
        final_sampled_route = {}

        final_segment_id = len(segment_mapping_dicts) - 1
        waypoint_count = 0
        sampled_waypoint_count = 0

        for i, segment in enumerate(segment_mapping_dicts):
            # at the start of the route, get the start of the segment
            if i == 0:
                final_mapping_dict["start"] = segment["start"]
            # at the end of the route, get the final point
            elif i == final_segment_id:
                final_mapping_dict["end"] = segment["end"]

            # add all the waypoints in the correct order
            for k, v in segment.items():
                if "waypoint_" in k:
                    final_mapping_dict["waypoint_{}".format(waypoint_count)] = segment[
                        k
                    ]
                    waypoint_count += 1

            sampled_route = sampled_routes[i]
            for k, v in sampled_route.items():
                final_sampled_route[sampled_waypoint_count] = v
                sampled_waypoint_count += 1

        return final_mapping_dict, final_sampled_route

    @staticmethod
    def sample_route_with_legs(route, npoints=1000):
        points_per_leg = [len(v["route"]) for k, v in route.items()]
        total_points = sum(points_per_leg)

        # get fraction of total points that need to be represented on each leg
        frac_per_leg = [
            max(1, np.round(npoints * (x / total_points), 0)) for x in points_per_leg
        ]

        sampled_points = {}
        for leg_id, route_info in route.items():
            total_points = int(points_per_leg[leg_id])
            total_sampled_points = int(frac_per_leg[leg_id])
            step_size = int(max(total_points // total_sampled_points, 1.0))
            route_sampled = [
                route_info["route"][idx] for idx in range(0, total_points, step_size)
            ]

            distance = route_info["distance"]
            duration = route_info["duration"]

            sampled_points[leg_id] = {
                "route": [
                    (float(x.split(",")[0]), float(x.split(",")[1]))
                    for x in route_sampled
                ],
                "duration": duration,
                "distance": distance,
            }

        return sampled_points
