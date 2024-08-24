import json
import uuid
import websocket
import random
import os
import io
import urllib.request
from PIL import Image

class ComfyUI:
    def __init__(self):
        self.server_address = '127.0.0.1:8188'
        

    def open_websocket_connection(self):
        client_id=str(uuid.uuid4())
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(self.server_address, client_id))
        return ws, self.server_address, client_id

    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(self.server_address, url_values)) as response:
            return response.read()

    def save_image(self, images, output_path, save_previews):
        for itm in images:
            directory = os.path.join(output_path, 'temp/') if itm['type'] == 'temp' and save_previews else output_path
            os.makedirs(directory, exist_ok=True)
            try:
                image = Image.open(io.BytesIO(itm['image_data']))
                image.save(os.path.join(directory, itm['file_name']))
            except Exception as e:
                print(f"Failed to save image {itm['file_name']}: {e}")

    def get_images(self, prompt_id, allow_preview = False):
        output_images = []

        history = self.get_history(prompt_id)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            output_data = {}
            if 'images' in node_output:
                for image in node_output['images']:
                    if allow_preview and image['type'] == 'temp':
                        preview_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                        output_data['image_data'] = preview_data
                    if image['type'] == 'output':
                        image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                        output_data['image_data'] = image_data
                output_data['file_name'] = image['filename']
                output_data['type'] = image['type']
            output_images.append(output_data)

        return output_images

    def track_progress(self, prompt, ws, prompt_id):
        node_ids = list(prompt.keys())
        finished_nodes = []

        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'progress':
                    data = message['data']
                    current_step = data['value']
                    print('In K-Sampler -> Step: ', current_step, ' of: ', data['max'])
                if message['type'] == 'execution_cached':
                    data = message['data']
                    for itm in data['nodes']:
                        if itm not in finished_nodes:
                            finished_nodes.append(itm)
                            print('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] not in finished_nodes:
                        finished_nodes.append(data['node'])
                        print('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')

                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue
        return

    def queue_prompt(self, prompt, client_id):
        p = {"prompt": prompt, "client_id": client_id}
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(self.server_address), data=data, headers=headers)
        return json.loads(urllib.request.urlopen(req).read())

    def prompt_to_image(self, workflow, positive_prompt, negative_prompt='', save_previews=False):
        from workflow_module import WorkflowManager
        workflow_manager = WorkflowManager()
        workflow_manager.run_workflow(workflow, positive_prompt, negative_prompt, './output/', save_previews)
        
    def prompt_to_video(self, video_path):
        from workflow_module import WorkflowManager
        workflow_manager = WorkflowManager()
        workflow_manager.run_workflow_with_video(video_path)