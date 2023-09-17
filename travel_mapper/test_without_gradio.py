from travel_mapper.TravelMapper import load_secrets, assert_secrets
from travel_mapper.TravelMapper import TravelMapperBase


def test(query=None):
    secrets = load_secrets()
    assert_secrets(secrets)

    if not query:
        query = """
        I want to do 2 week trip from Berkeley CA to New York City.
        I want to visit national parks and cities with good food.
        I want use a rental car and drive for no more than 5 hours on any given day.
        """

    mapper = TravelMapperBase(
        openai_api_key=secrets["OPENAI_API_KEY"],
        google_maps_key=secrets["GOOGLE_MAPS_API_KEY"],
        google_palm_api_key=secrets["GOOGLE_PALM_API_KEY"],
    )

    mapper.parse(query, make_map=True)
