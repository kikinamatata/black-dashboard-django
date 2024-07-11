import uuid
import json
import requests
import urllib.parse


class ImageVO():
    name: str
    subfolder: str
    type: str


class ClientServiceBase:
    
    upload_image_url = None
    get_history_url = None
    get_image_url = None
    server_address = None
    queue_prompt_url = None
    remove_image_url = None
    status_websocket_url = None
    status_get_url = None

    client_id = str(uuid.uuid4())

    def update_server_url(self, server_url):
        self.server_address = "https://" + server_url if "cloudflare" in server_url else "http://" + server_url
        self.queue_prompt_url = "{}/prompt".format(self.server_address)
        self.get_image_url = "{}/view".format(self.server_address)
        self.get_history_url = "{}/history".format(self.server_address)
        self.upload_image_url = "{}/upload/image".format(self.server_address)
        self.remove_image_url = "{}/remove".format(self.server_address)
        self.status_websocket_url = "ws://{}/ws?clientId={}".format(server_url, self.client_id)
        self.status_get_url = "{}/prompt_status/".format(self.server_address)

    def get_image(self, img: ImageVO):
        data = {"filename": img.name, "subfolder": img.subfolder, "type": img.type}
        url_values = urllib.parse.urlencode(data)
        with requests.get(self.get_image_url + "?{}".format(url_values)) as response:
            return response.content

    def remove_image(self, img: ImageVO):
        response_json = {"name": img.name, "subfolder": img.subfolder, "type": img.type}
        response = requests.post(self.remove_image_url, data=response_json)
        if response.status_code == 200:
            print("Image removed successfully!")
        else:
            print("Image removal failed")

