from langchain.chains import LLMChain, SequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import GooglePalm
from travel_mapper.agent.templates import (
    ValidationTemplate,
    ItineraryTemplate,
    MappingTemplate,
)
from travel_mapper.constants import MODEL_NAME, TEMPERATURE
import openai
import logging
import time

logging.basicConfig(level=logging.INFO)


class Agent(object):
    def __init__(
        self,
        open_ai_api_key,
        google_palm_api_key,
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        debug=True,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        if "gpt" in model:
            # model is open ai
            self.logger.info("Base LLM is OpenAI chatGPT series")
            openai.api_key = open_ai_api_key
            self.chat_model = ChatOpenAI(model=model, temperature=temperature)
        elif "bison-001" in model:
            # model is google palm
            self.logger.info("Base LLM is Google Palm")
            self.chat_model = GooglePalm(
                model_name=model,
                temperature=temperature,
                google_api_key=google_palm_api_key,
            )

        self._palm_key = google_palm_api_key
        self._openai_key = open_ai_api_key

        self.validation_prompt = ValidationTemplate()
        self.itinerary_prompt = ItineraryTemplate()
        self.mapping_prompt = MappingTemplate()

        self.validation_chain = self._set_up_validation_chain(debug)
        self.agent_chain = self._set_up_agent_chain(debug)

    def update_model_family(self, new_model):
        """

        Parameters
        ----------
        new_model

        Returns
        -------

        """

        if "gpt" in new_model:
            # model is open ai
            self.logger.info("Base LLM is OpenAI chatGPT series")
            self.chat_model = ChatOpenAI(model=new_model, temperature=TEMPERATURE)
        elif "bison-001" in new_model:
            # model is google palm
            self.logger.info("Base LLM is Google Palm")
            self.chat_model = GooglePalm(
                model_name=new_model,
                temperature=TEMPERATURE,
                google_api_key=self._palm_key,
            )

    def _set_up_validation_chain(self, debug=True):
        """

        Parameters
        ----------
        debug

        Returns
        -------

        """
        validation_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.validation_prompt.chat_prompt,
            output_parser=self.validation_prompt.parser,
            output_key="validation_output",
            verbose=debug,
        )

        overall_chain = SequentialChain(
            chains=[validation_agent],
            input_variables=["query", "format_instructions"],
            output_variables=["validation_output"],
            verbose=debug,
        )

        return overall_chain

    def _set_up_agent_chain(self, debug=True):
        """

        Parameters
        ----------
        debug

        Returns
        -------

        """
        travel_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.itinerary_prompt.chat_prompt,
            verbose=debug,
            output_key="agent_suggestion",
        )

        parser = LLMChain(
            llm=self.chat_model,
            prompt=self.mapping_prompt.chat_prompt,
            output_parser=self.mapping_prompt.parser,
            verbose=debug,
            output_key="mapping_list",
        )

        overall_chain = SequentialChain(
            chains=[travel_agent, parser],
            input_variables=["query", "format_instructions"],
            output_variables=["agent_suggestion", "mapping_list"],
            verbose=debug,
        )

        return overall_chain

    def suggest_travel(self, query):
        """

        Parameters
        ----------
        query

        Returns
        -------

        """
        self.logger.info("Validating query")
        t1 = time.time()
        self.logger.info(
            "Calling validation (model is {}) on user input".format(
                self.chat_model.model_name
            )
        )
        validation_result = self.validation_chain(
            {
                "query": query,
                "format_instructions": self.validation_prompt.parser.get_format_instructions(),
            }
        )

        validation_test = validation_result["validation_output"].dict()
        t2 = time.time()
        self.logger.info("Time to validate request: {}".format(round(t2 - t1, 2)))

        if validation_test["plan_is_valid"].lower() == "no":
            self.logger.warning("User request was not valid!")
            print("\n######\n Travel plan is not valid \n######\n")
            print(validation_test["updated_request"])
            return None, None, validation_result

        else:
            # plan is valid
            self.logger.info("Query is valid")
            self.logger.info("Getting travel suggestions")
            t1 = time.time()

            self.logger.info(
                "User request is valid, calling agent (model is {})".format(
                    self.chat_model.model_name
                )
            )

            agent_result = self.agent_chain(
                {
                    "query": query,
                    "format_instructions": self.mapping_prompt.parser.get_format_instructions(),
                }
            )

            trip_suggestion = agent_result["agent_suggestion"]
            list_of_places = agent_result["mapping_list"].dict()
            t2 = time.time()
            self.logger.info("Time to get suggestions: {}".format(round(t2 - t1, 2)))

            return trip_suggestion, list_of_places, validation_result
