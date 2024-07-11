
from .client_service import ClientService
import gradio as gr

class VideoGallery():
    input_image: gr.Image = None
    user_prompt: gr.Textbox = None
    submit_button: gr.Button = None


    def video_generation_tab(self):
        client_service = ClientService()
        with gr.Row():
                    with gr.Column():
                        self.input_image = gr.Image(type='filepath')
                        with gr.Accordion(label="Advanced", open=False):
                            self.user_prompt = gr.Textbox(label='Prompt')
                        self.submit_button = gr.Button(value="Generate")
                    with gr.Column():
                        output = gr.Video()
        self.submit_button.click(client_service.generate_video, inputs=[self.input_image, self.user_prompt],
                                          outputs=output)