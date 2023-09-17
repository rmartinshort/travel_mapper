#!/usr/bin/env python

import sys
import gradio as gr
from travel_mapper.TravelMapper import TravelMapperForUI, load_secrets, assert_secrets
from travel_mapper.user_interface.capture_logs import PrintLogCapture
from travel_mapper.user_interface.utils import generate_generic_leafmap
from travel_mapper.user_interface.constants import EXAMPLE_QUERY


def read_logs():
    sys.stdout.flush()
    with open("output.log", "r") as f:
        return f.read()


def main():
    """

    Returns
    -------

    """
    secrets = load_secrets()
    assert_secrets(secrets)

    travel_mapper = TravelMapperForUI(
        openai_api_key=secrets["OPENAI_API_KEY"],
        google_maps_key=secrets["GOOGLE_MAPS_API_KEY"],
        google_palm_api_key=secrets["GOOGLE_PALM_API_KEY"],
    )
    sys.stdout = PrintLogCapture("output.log")

    # build the UI in gradio
    app = gr.Blocks()

    generic_map = generate_generic_leafmap()

    with app:
        gr.Markdown("## Generate travel suggestions")
        with gr.Tabs():
            with gr.TabItem("Generate with map"):
                with gr.Row():
                    with gr.Column():
                        text_input_map = gr.Textbox(
                            EXAMPLE_QUERY, label="Travel query", lines=4
                        )

                        radio_map = gr.Radio(
                            value="gpt-3.5-turbo",
                            choices=["gpt-3.5-turbo", "gpt-4", "models/text-bison-001"],
                            label="models",
                        )

                        query_validation_text = gr.Textbox(
                            label="Query validation information", lines=2
                        )
                        # ideally we want to print logs to the app too
                        # logs = gr.Textbox(label="Logs")
                        # app.load(read_logs, None, logs, every=1)
                    with gr.Column():
                        # place where the map will appear
                        map_output = gr.HTML(generic_map, label="Travel map")
                        # place where the suggested trip will appear
                        itinerary_output = gr.Textbox(
                            value="Your itinerary will appear here",
                            label="Itinerary suggestion",
                            lines=3,
                        )
                map_button = gr.Button("Generate")
            with gr.TabItem("Generate without map"):
                with gr.Row():
                    with gr.Column():
                        text_input_no_map = gr.Textbox(
                            value=EXAMPLE_QUERY, label="Travel query", lines=3
                        )

                        radio_no_map = gr.Radio(
                            value="gpt-3.5-turbo",
                            choices=["gpt-3.5-turbo", "gpt-4", "models/text-bison-001"],
                            label="Model choices",
                        )

                        query_validation_no_map = gr.Textbox(
                            label="Query validation information", lines=2
                        )
                    with gr.Column():
                        text_output_no_map = gr.Textbox(
                            value="Your itinerary will appear here",
                            label="Itinerary suggestion",
                            lines=3,
                        )
                text_button = gr.Button("Generate")

        map_button.click(
            travel_mapper.generate_with_leafmap,
            inputs=[text_input_map, radio_map],
            outputs=[map_output, itinerary_output, query_validation_text],
        )
        text_button.click(
            travel_mapper.generate_without_leafmap,
            inputs=[text_input_no_map, radio_no_map],
            outputs=[text_output_no_map, query_validation_no_map],
        )

    app.launch()


if __name__ == "__main__":
    main()
