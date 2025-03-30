import os
import tempfile
import gradio as gr
import traceback
from pathlib import Path
from inference import seed_everything, run, StreamSDK

# TensorRT版本检查
def check_tensorrt_version():
    try:
        import tensorrt as trt
        return trt.__version__
    except ImportError:
        return "未安装"
    except Exception as e:
        return f"检查失败: {str(e)}"

# 初始化SDK
def initialize_sdk(data_root, cfg_pkl):
    try:
        return StreamSDK(cfg_pkl, data_root)
    except AssertionError as e:
        trt_version = check_tensorrt_version()
        error_msg = (
            f"TensorRT引擎初始化失败。可能是TensorRT版本不匹配问题。\n"
            f"当前TensorRT版本: {trt_version}\n"
            f"解决方案:\n"
            f"1. 确保您安装了与模型兼容的TensorRT版本 (参考README.md)\n"
            f"2. 您可能需要使用与模型创建时相同版本的TensorRT重新转换模型\n"
            f"3. 或者下载与您当前TensorRT版本兼容的模型文件"
        )
        raise RuntimeError(error_msg) from e
    except Exception as e:
        raise e

# 视频合成函数
def synthesize_video(audio, image, use_seed=False, seed=1024, fade_in=-1, fade_out=-1, data_root=None, cfg_pkl=None):
    try:
        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        
        # 检查输入
        if audio is None:
            return None, "错误：请上传音频文件"
        
        if image is None:
            return None, "错误：请上传图片"
        
        # 确定文件扩展名
        audio_ext = os.path.splitext(audio)[1].lower() if isinstance(audio, str) else ".wav"
        image_ext = os.path.splitext(image)[1].lower() if isinstance(image, str) else ".png"
        
        # 保存上传的音频和图像
        audio_path = os.path.join(temp_dir, f"input_audio{audio_ext}")
        image_path = os.path.join(temp_dir, f"input_image{image_ext}")
        output_path = os.path.join(temp_dir, "output_video.mp4")
        
        # 处理音频和图像
        if isinstance(audio, str):
            # 如果是文件路径，则复制文件
            import shutil
            shutil.copy(audio, audio_path)
        else:
            # 否则保存文件
            audio.save(audio_path)
            
        if isinstance(image, str):
            # 如果是文件路径，则复制文件
            import shutil
            shutil.copy(image, image_path)
        else:
            # 否则保存文件
            image.save(image_path)
        
        # 设置默认路径
        if not data_root:
            data_root = "./checkpoints/ditto_trt_Ampere_Plus"
        if not cfg_pkl:
            cfg_pkl = "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt.pkl"
        
        # 检查模型文件是否存在
        if not os.path.exists(data_root):
            return None, f"错误：模型目录不存在 - {data_root}"
        if not os.path.exists(cfg_pkl):
            return None, f"错误：配置文件不存在 - {cfg_pkl}"
        
        # 可选：设置随机种子
        if use_seed:
            seed_everything(seed)
        
        try:
            # 初始化SDK
            sdk = initialize_sdk(data_root, cfg_pkl)
            
            # 设置额外参数
            more_kwargs = {
                "setup_kwargs": {},
                "run_kwargs": {
                    "fade_in": fade_in,
                    "fade_out": fade_out,
                    "ctrl_info": {}
                }
            }
            
            # 运行合成
            run(sdk, audio_path, image_path, output_path, more_kwargs)
            
            # 检查输出文件是否存在
            if not os.path.exists(output_path):
                return None, "错误：视频合成失败，未生成输出文件"
                
            return output_path, "合成成功！"
            
        except RuntimeError as e:
            if "TensorRT" in str(e):
                return None, str(e)
            else:
                raise e
                
    except Exception as e:
        error_msg = f"处理时出错: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return None, error_msg

# 显示系统信息
def show_system_info():
    import platform
    import sys
    
    info = []
    info.append(f"操作系统: {platform.system()} {platform.version()}")
    info.append(f"Python版本: {sys.version}")
    
    # 检查CUDA
    try:
        import torch
        info.append(f"PyTorch版本: {torch.__version__}")
        info.append(f"CUDA可用: {'是' if torch.cuda.is_available() else '否'}")
        if torch.cuda.is_available():
            info.append(f"CUDA版本: {torch.version.cuda}")
            info.append(f"GPU型号: {torch.cuda.get_device_name(0)}")
    except ImportError:
        info.append("PyTorch: 未安装")
    
    # 检查TensorRT
    trt_version = check_tensorrt_version()
    info.append(f"TensorRT版本: {trt_version}")
    
    return "\n".join(info)

# 创建Gradio界面
def create_interface():
    with gr.Blocks(title="Ditto 视频合成") as demo:
        gr.Markdown("# Ditto 视频合成系统")
        gr.Markdown("上传音频和图片，自动合成会说话的人物视频")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(type="filepath", label="上传音频文件 (WAV格式)", elem_id="audio_input")
                image_input = gr.Image(type="filepath", label="上传图片", elem_id="image_input")
                
                with gr.Accordion("高级设置", open=False):
                    use_seed = gr.Checkbox(label="使用固定随机种子", value=False)
                    seed = gr.Slider(minimum=0, maximum=10000, value=1024, step=1, label="随机种子值")
                    fade_in = gr.Slider(minimum=-1, maximum=100, value=-1, step=1, label="淡入帧数 (-1表示不使用)")
                    fade_out = gr.Slider(minimum=-1, maximum=100, value=-1, step=1, label="淡出帧数 (-1表示不使用)")
                    
                    with gr.Accordion("模型设置", open=False):
                        data_root = gr.Textbox(label="模型目录路径", value="./checkpoints/ditto_trt_Ampere_Plus", 
                                              info="包含模型文件的目录路径")
                        cfg_pkl = gr.Textbox(label="配置文件路径", value="./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt.pkl", 
                                            info="模型配置文件的路径")
                
                submit_btn = gr.Button("开始合成", variant="primary")
            
            with gr.Column():
                output_video = gr.Video(label="合成结果")
                output_msg = gr.Textbox(label="处理状态", interactive=False)
        
        # 我们不使用Examples功能，因为它可能导致路径问题
        # 而是添加一个指向示例的说明
        gr.Markdown("""
        ## 示例
        您可以使用以下示例文件进行测试：
        - 音频示例：`./example/audio/sample1.wav`, `./example/audio/sample2.wav`
        - 图像示例：`./example/images/sample1.jpg`, `./example/images/sample2.jpg`
        
        请手动选择这些文件上传。
        """)
        
        # 添加系统信息区域
        with gr.Accordion("系统信息", open=False):
            system_info = gr.Textbox(label="环境信息", interactive=False)
            refresh_btn = gr.Button("刷新系统信息")
            refresh_btn.click(fn=show_system_info, inputs=[], outputs=system_info)
        
        submit_btn.click(
            fn=synthesize_video,
            inputs=[audio_input, image_input, use_seed, seed, fade_in, fade_out, data_root, cfg_pkl],
            outputs=[output_video, output_msg]
        )
        
        # 添加CSS样式
        gr.HTML("""
        <style>
        .gradio-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .footer {
            margin-top: 20px;
            text-align: center;
            color: #666;
        }
        </style>
        """)
        
        # 添加页脚
        gr.HTML("""
        <div class="footer">
            <p>Ditto 视频合成系统 | Powered by Gradio</p>
        </div>
        """)
        
    return demo

if __name__ == "__main__":
    # 创建额外的requirements文件以安装gradio
    if not os.path.exists("requirements_webui.txt"):
        with open("requirements_webui.txt", "w") as f:
            f.write("gradio>=3.50.2\n")
        print("Created requirements_webui.txt - Please run 'pip install -r requirements_webui.txt' to install Gradio")
    
    # 检查example目录
    example_dir = Path("./example")
    if not example_dir.exists():
        # 创建示例目录结构
        (example_dir / "audio").mkdir(parents=True, exist_ok=True)
        (example_dir / "images").mkdir(parents=True, exist_ok=True)
        print("Created example directory structure. Please add sample files to use examples.")
    
    # 显示初始系统信息
    print("="*50)
    print("系统信息:")
    print(show_system_info())
    print("="*50)
    
    # 查找可用端口
    def find_free_port(start_port=7860, max_attempts=100):
        import socket
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:
                    return port
        return None
    
    # 使用动态端口
    port = find_free_port()
    if port is None:
        print("警告: 无法找到可用端口，将尝试使用默认端口7860")
        port = 7860
    else:
        print(f"使用端口: {port}")
    
    # 启动Gradio应用
    demo = create_interface()
    demo.launch(share=False, server_name="127.0.0.1", server_port=port, inbrowser=True) 