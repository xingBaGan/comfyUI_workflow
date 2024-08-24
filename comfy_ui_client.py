from comfy_ui_module import ComfyUI

comfy = ComfyUI()
# 加载工作流
# comfy.prompt_to_image('./workflow_base.json', 'beautiful scenery nature glass bottle landscape, , purple galaxy bottle,', 'text, watermark', True)
# comfy.prompt_to_video(r"e:\animation_workspace\remove_bg.mp4")
video = comfy.get_first_of_video_history()
local_file_path = 'output_video.mp4'
if video:
    video_res = comfy.get_output(video['filename'], video['subfolder'], video['type'])
    # 将Content-Type为video/mp4的响应体保存为视频文件
    with open(local_file_path, 'wb') as f:
        f.write(video_res)
    print(f'视频已成功保存到：{local_file_path}')
else:
    print("没有找到视频历史记录")