import unittest
from travel_mapper.agent.Agent import Agent
from travel_mapper.TravelMapper import load_secrets, assert_secrets
import langchain

DEBUG = True


class TestAgentMethods(unittest.TestCase):
    def setUp(self):
        self.debug = True
        secrets = load_secrets()
        assert_secrets(secrets)

        self.agent = Agent(
            open_ai_api_key=secrets["OPENAI_API_KEY"],
            google_palm_api_key=secrets["GOOGLE_PALM_API_KEY"],
            debug=True,
        )

    def test_update_model_family(self):
        # switch model family to google palm
        self.agent.update_model_family("models/text-bison-001")
        self.assertEqual(
            type(self.agent.chat_model), langchain.llms.google_palm.GooglePalm
        )
        self.assertEqual(self.agent.chat_model.model_name, "models/text-bison-001")

        # switch model family to chat gpt
        self.agent.update_model_family("gpt-3.5-turbo")
        self.assertEqual(
            type(self.agent.chat_model), langchain.chat_models.openai.ChatOpenAI
        )
        self.assertEqual(self.agent.chat_model.model_name, "gpt-3.5-turbo")

    @unittest.skipIf(DEBUG, "debugging_other_tests")
    def test_validation_chain(self):
        validation_chain = self.agent._set_up_validation_chain(debug=True)

        # not a reasonable request
        q1 = "fly to the moon"
        q1_res = validation_chain(
            {
                "query": q1,
                "format_instructions": self.agent.validation_prompt.parser.get_format_instructions(),
            }
        )
        q1_out = q1_res["validation_output"].dict()
        self.assertEqual(q1_out["plan_is_valid"], "no")

        # not a reasonable request
        q2 = "1 day road trip from Chicago to Brazilia"
        q2_res = validation_chain(
            {
                "query": q2,
                "format_instructions": self.agent.validation_prompt.parser.get_format_instructions(),
            }
        )
        q2_out = q2_res["validation_output"].dict()
        self.assertEqual(q2_out["plan_is_valid"], "no")

        # a reasonable request
        q3 = "1 week road trip from Chicago to Mexico city"
        q3_res = validation_chain(
            {
                "query": q3,
                "format_instructions": self.agent.validation_prompt.parser.get_format_instructions(),
            }
        )
        q3_out = q3_res["validation_output"].dict()
        self.assertEqual(q3_out["plan_is_valid"], "yes")

    def test_agent_chain(self):
        agent_chain = self.agent._set_up_agent_chain(debug=True)

        q1 = """
        5 day roadtrip from Las Vegas NV to Houston TX, stopping at 
        pretty national parks with desert and mountain views.
        While in Texas I also want to try a few BBQ restaurants
        """
        agent_result = agent_chain(
            {
                "query": q1,
                "format_instructions": self.agent.mapping_prompt.parser.get_format_instructions(),
            }
        )

        trip_suggestion = agent_result["agent_suggestion"]
        list_of_places = agent_result["mapping_list"].dict()

        self.assertIsInstance(trip_suggestion, str)
        self.assertIsInstance(list_of_places, dict)
        self.assertGreater(len(list_of_places["waypoints"]), 2)
        self.assertEqual(list_of_places["start"], "Las Vegas, NV")
        self.assertEqual(list_of_places["end"], "Houston, TX")


if __name__ == "__main__":
    unittest.main()
