from comfy_ui_module import ComfyUI

comfy = ComfyUI()
# 加载工作流
# comfy.prompt_to_image('./workflow_base.json', 'beautiful scenery nature glass bottle landscape, , purple galaxy bottle,', 'text, watermark', True)
comfy.prompt_to_video(r"e:\animation_workspace\remove_bg.mp4")

