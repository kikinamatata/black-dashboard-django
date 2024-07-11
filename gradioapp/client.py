import gradio as gr
from .theme_seafoam import Seafoam
from threading import Thread
from .style_gallery import StyleGallery
from .video_gallery import VideoGallery
from django.conf import settings
import os

seafoam = Seafoam()

import yaml

class Client_UI():
    iface: gr.Blocks = None
    def __init__(self,server_url, testing_ui=False):

        # with gr.Blocks(theme=gr.themes.Default(),css=".gradio .input_gallery { background-color: red; color: white; }") as self.iface:
        with gr.Blocks(theme="HaleyCH/HaleyCH_Theme",css=".gradio .input_gallery { background-color: red; color: white; }") as self.iface:

            gr.Markdown("Time MachineX")  # Title
            with gr.Tab(label="Image Generation"):
                style_gallery = StyleGallery(server_url=server_url)
                style_gallery.image_generation_tab()
            with gr.Tab(label="Video Generation"):
                video_gallery = VideoGallery()  # VideoGallery class from video_gallery.py
                video_gallery.video_generation_tab()
                

    def launch_gradio(self):
        self.iface.queue().launch(share=True, inline=False, server_port=7750)

def start_gradio_interface():
    with open(os.path.join(settings.BASE_DIR,'gradioapp','config.yml'), 'r') as stream:
        config = yaml.safe_load(stream)
    server_url = config["server_url"]
    testing_ui = False
    client_ui = Client_UI(server_url=server_url, testing_ui=testing_ui)
    thread = Thread(target=client_ui.launch_gradio)
    thread.start()
    
if __name__ == "__main__":
     
     with open('config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
        # config = load_config()
        # server_url = "127.0.0.1:8188"
        server_url =config["server_url"]
        print("server_url: ", server_url)
        testing_ui = False
        client_ui = Client_UI(server_url=server_url, testing_ui=testing_ui)
        client_ui.launch_gradio()
