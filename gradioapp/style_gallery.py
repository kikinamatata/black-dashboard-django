import gradio as gr
from .client_service import ClientService
from .client_service import ImageStyleVO, StyleGroupVO
from .theme_seafoam import Seafoam
import json

seafoam = Seafoam()

import yaml

class StyleGallery():
    input_image: gr.Image = None
    submit_button: gr.Button = None
    output_painting: gr.Image = None
    iface: gr.Blocks = None
    reference_image_textbox: gr.Textbox = None
    gallery_list: list[gr.Gallery] = []
    style_group_list: list[StyleGroupVO] = []
    client_service = None

    def __init__(self,server_url):
        self.client_service = ClientService()
        self.client_service.update_server_url(server_url)

    def change_reference_image(self, sd: gr.SelectData):
        selected_gallery: gr.Gallery = sd.target
        image_name = ''
        for index, gallery in enumerate(self.gallery_list):
            # print(f"Gallery #{index + 1}:")
            if selected_gallery == gallery:
                print(sd.value)
                print(sd.value['caption'])
                group = self.style_group_list[index]
                print(f'index of gallery {index}')
                style:ImageStyleVO = group.items[sd.index]
                image_name = style.name

                print(image_name)
            else:
                gallery.selected_index = None
                gallery.value = gallery.value
        return image_name
    
    def image_generation_tab(self):
        self.style_group_list = self.client_service.thumbnail()
        with gr.Row():
            with gr.Column(min_width=100):
                for style_group in self.style_group_list:
                    image_list = []
                    for image_style in style_group.items:
                        image_list.append((image_style.image, image_style.id))
                    gallery = gr.Gallery(label=style_group.name, value=image_list, allow_preview=False, rows=1,
                                         columns=4, height=185)
                    self.gallery_list.append(gallery)
            with gr.Column(min_width=100):
                self.reference_image_textbox = gr.Textbox(label='Reference Image', interactive=False,
                                                          visible=False)
                self.output_painting = gr.Image(label="Generated", height=500,
                                                min_width=500)
                with gr.Row(equal_height=True):
                    self.input_image = gr.Image(label='Your Image', type='filepath', height=270, width=270)
                    self.submit_button = gr.Button(value="Generate", scale=0)

        self.submit_button.click(self.client_service.generate_image,
                                 inputs=[self.input_image, self.reference_image_textbox],
                                 outputs=self.output_painting)
        for gallery in self.gallery_list:
            gallery.select(self.change_reference_image, None, self.reference_image_textbox)