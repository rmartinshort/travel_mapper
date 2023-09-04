from travel_mapper.TravelMapper import load_secets, assert_secrets
from travel_mapper.TravelMapper import TravelMapper


def test(query=None):
    secrets = load_secets()
    assert_secrets(secrets)

    if not query:
        query = """
        I want to do 3 week trip from Berkeley CA to New York City.
        I want to visit national parks and cities with good food.
        I want use a rental car and drive for no more than 3 hours on any given day. 
        """

    mapper = TravelMapper(
        openai_api_key=secrets["OPENAI_API_KEY"],
        google_maps_key=secrets["GOOGLE_MAPS_API_KEY"],
    )

    mapper.parse(query, make_map=True)
