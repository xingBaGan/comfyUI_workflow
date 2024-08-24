import json
import random
from comfy_ui_module import ComfyUI

class WorkflowManager:
    def __init__(self):
        self.comfy_ui = ComfyUI()

    def load_workflow(self, workflow_path):
        try:
            with open(workflow_path, 'r', encoding='utf-8') as file:
                workflow = json.load(file)
                self.prompt = workflow
                self.id_to_class_type = {id: details['class_type'] for id, details in self.prompt.items()}
                return json.dumps(workflow)
        except FileNotFoundError:
            print(f"文件 {workflow_path} 未找到。")
            return None
        except json.JSONDecodeError:
            print(f"文件 {workflow_path} 包含无效的 JSON。")
            return None
        except UnicodeDecodeError:
            print(f"文件 {workflow_path} 编码错误，尝试使用其他编码。")
            try:
                with open(workflow_path, 'r', encoding='gbk') as file:
                    workflow = json.load(file)
                    return json.dumps(workflow)
            except:
                print(f"无法读取文件 {workflow_path}，请检查文件编码。")
                return None
    def prepare_prompt(self, workflow, positive_prompt='', negative_prompt=''):
        k_sampler_id = next(key for key, value in self.id_to_class_type.items() if value == 'KSampler')
        self.prompt[k_sampler_id]['inputs']['seed'] = random.randint(10**14, 10**15 - 1)
        
        if positive_prompt != '':
            positive_input_id = self.prompt[k_sampler_id]['inputs']['positive'][0]
            self.prompt[positive_input_id]['inputs']['text'] = positive_prompt

        if negative_prompt != '':
            negative_input_id = self.prompt[k_sampler_id]['inputs']['negative'][0]
            self.prompt[negative_input_id]['inputs']['text'] = negative_prompt

        return self.prompt

    def prepare_video_params(self, video_path):
        VHS_LoadVideo_id = next(key for key, value in self.id_to_class_type.items() if value == 'VHS_LoadVideo')
        if video_path != '':
            video_id = self.prompt[VHS_LoadVideo_id]['inputs']['video']
            self.prompt[VHS_LoadVideo_id]['inputs']['video'] = video_path
        return self.prompt

    def execute_prompt(self, prompt):
        ws, _, client_id = self.comfy_ui.open_websocket_connection()
        prompt_id = self.comfy_ui.queue_prompt(prompt, client_id)['prompt_id']
        self.comfy_ui.track_progress(prompt, ws, prompt_id)
        return ws, prompt_id

    def generate_image(self, prompt, output_path, save_previews=False):
        try:
            ws, prompt_id = self.execute_prompt(prompt)
            images = self.comfy_ui.get_images(prompt_id, save_previews)
            self.comfy_ui.save_image(images, output_path, save_previews)
        except Exception as e:
            print(f"生成图像时发生错误：{e}")
        finally:
            ws.close()

    def generate_video(self, prompt):
        try:
            ws, prompt_id = self.execute_prompt(prompt)
            # images = self.comfy_ui.get_images(prompt_id, save_previews)
            # self.comfy_ui.save_image(images, output_path, save_previews)
        except Exception as e:
            print(f"生成图像时发生错误：{e}")
        finally:
            ws.close()

    def run_workflow(self, workflow_path, positive_prompt, negative_prompt='', output_path='./output/', save_previews=False):
        workflow = self.load_workflow(workflow_path)
        if workflow:
            prompt = self.prepare_prompt(workflow, positive_prompt, negative_prompt)
            self.generate_image(prompt, output_path, save_previews)

    def run_workflow_with_video(self, video_path, workflow_path = './workflow_api.json', output_path='./output/'):
        workflow = self.load_workflow(workflow_path)
        if workflow:
            prompt = self.prepare_video_params(video_path)
            self.generate_video(prompt)