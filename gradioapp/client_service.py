import websocket
import io
import base64
import gradio as gr
from PIL import Image
import requests
import json

import urllib.parse
from .client_service_base import ClientServiceBase


class ImageStyleVO():
    id: str
    name: str
    image: Image
    style:str


class StyleGroupVO():
    style: str
    name: str
    items: list[ImageStyleVO]

class Queue():
    ref_name: str
    image_path: str
    def __init__(self, ref_name, image_path):
        self.ref_name = ref_name
        self.image_path = image_path
    
class ClientService(ClientServiceBase):

    in_progress = False
    queue_list: list[Queue] = []
    thumbnail_url = None
    queue_prompt_digital_url = None
    queue_prompt_video_url = None
    get_view_extention_url = None
    response_json = None
    style_group_list: list[StyleGroupVO] = None

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ClientService, cls).__new__(cls, *args, **kwargs)
        return cls._instance


    def update_server_url(self, server_url):
        super().update_server_url(server_url)
        self.queue_prompt_digital_url = "{}/digital-painting".format(self.server_address)
        self.queue_prompt_video_url = "{}/digital-video".format(self.server_address)
        self.get_view_extention_url = "{}/view_extention".format(self.server_address)
        self.thumbnail_url = "{}/thumbnails".format(self.server_address)
    
    def thumbnail(self) -> list[StyleGroupVO]:
        response = requests.get(self.thumbnail_url)
        print(response)
        style_group_json = response.json()['thumbnails']
        self.style_group_list: list[StyleGroupVO] = []
        style_id = 1
        for group in style_group_json:
            style_group = StyleGroupVO()
            style_group.name = group['name']
            style_group.style = group['style']
            style_group.items = []
            for file in group['items']:
                image = Image.open(io.BytesIO(base64.b64decode(file['data'])))
                image_style = ImageStyleVO()
                image_style.id = f"{style_id}"
                style_id += 1
                image_style.name = file['filename']
                image_style.style = file['style']
                image_style.image = image
                style_group.items.append(image_style)
            self.style_group_list.append(style_group)

        return self.style_group_list

    def queue_prompt_digital(self, image_path, ref_name):
       
        
        data = {
            "client_id": self.client_id,
            "ref_name": ref_name
        }
        print(data)
        print('request data', data)

        files = {"image": open(image_path, 'rb')}
        print('including  image data send')
        response = requests.post(self.queue_prompt_digital_url, data=data, files=files)
        if response.status_code != 200:
            # self.in_progress = False
            print("Error in digital painting prompt queueing:", response.text)
        else:
            
            response_json = response.json()
            print('Response :', response_json)
            print("Image uploaded successfully!")
            return response_json

    def get_images(self, prompt_id) -> list[Image.Image]:
        data = {"prompt_id": prompt_id}
        url_values = urllib.parse.urlencode(data)
        img_arr = []
        with requests.get(self.get_view_extention_url + "?{}".format(url_values)) as response:
            image_data = response.json()
            im = Image.open(io.BytesIO(base64.b64decode(image_data['data'])))
            img_arr.append(im)
            print(len(img_arr))
        
        return img_arr

    def get_status_websocket(self, prompt_id, pr):
        ws = websocket.WebSocket()
        ws.connect(self.status_websocket_url)
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                print("websocket message :",message)
                if message['type'] == 'progress':
                    data = message['data']
                    pr((data['value'], data['max']), desc=message['type'])
                else:
                    pr(progress=1, desc=message['type'])
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break
            else:
                continue
        ws.close()    

    def get_status_rest(self, prompt_id, pr):
        while True:
            response = requests.get(self.status_get_url + prompt_id)
            response_json = response.json()
            if response_json['status'] == 200:
                pr((response_json['value'], response_json['max']), desc="executing")
                if response_json['value'] == response_json['max']:
                    break
        while True:
            response = requests.get(self.status_get_url + prompt_id)
            response_json = response.json()
            print(response_json)
            if response_json['status'] == 'executing':
                break


    def get_style_from_group_list(self, ref_name):
        for group in self.style_group_list:
            for item in group.items:
                if item.name == ref_name:
                    return item
        return self.style_group_list[0].items[0]
    
    def generate_image(self, image_path, ref_name, status_method='websocket', pr=gr.Progress()):
         # gr.Warning("Please wait while the image is being generated.")
        # if self.in_progress:
        #     gr.Error("Please wait while the image is being generated.")
        #     return
        # self.in_progress = True
        styleVO:ImageStyleVO = self.get_style_from_group_list(ref_name)
        print(ref_name, image_path)
        response = self.queue_prompt_digital(image_path, styleVO.name)
        print(response)
        prompt_id = response['prompt_id']
        if status_method == "websocket":
            self.get_status_websocket(prompt_id, pr)
        else:
            self.get_status_rest(prompt_id, pr)
        img_list = self.get_images(prompt_id)
        print("Image generated successfully!")
        # self.in_progress = False
        gr.Info("Image generated successfully! You can try next image.")
        return img_list[-1]
        
    def generate_video(self, image_path, user_prompt, status_method='websocket', pr=gr.Progress()):
        response = self.queue_prompt_video(user_prompt, image_path)
        prompt_id = response['prompt_id']
        if status_method == "websocket":
            self.get_status_websocket(prompt_id, pr)
        else:
            self.get_status_rest(prompt_id, pr)

    def queue_prompt_video(self, image_path, ref_name):
        data = {
            "client_id": self.client_id,
            "user_prompt": "",
            "overwrite": None,
            "subfolder": "",
            "type": None
        }
        files = {"image": open(image_path, 'rb')}
        req = requests.post(self.queue_prompt_video_url, data=data, files=files)
        if req.status_code != 200:
            print("Error in digital painting prompt queueing:", req.text)
        else:
            
            print("Image uploaded successfully!")
            response = req.json()
            return response