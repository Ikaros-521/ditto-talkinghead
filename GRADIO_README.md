# Ditto视频合成Gradio界面使用说明

## 简介

Ditto视频合成系统是一个能够将音频和静态图像合成为说话人物视频的工具。本项目提供了一个基于Gradio的图形界面，使您能够轻松地使用这一功能而无需编写代码。

## 安装与使用

### TensorRT 8.6.1安装（重要！）

本项目依赖于TensorRT 8.6.1版本，请按照以下步骤安装：

1. 访问NVIDIA官方网站下载TensorRT 8.6.1：https://developer.nvidia.com/tensorrt-getting-started
   - 需要注册NVIDIA开发者账户
   - 选择与您系统匹配的版本（Windows x64）
   - 选择与您CUDA版本兼容的TensorRT版本（例如，CUDA 11.x对应的TensorRT 8.6.1）
   - 如果链接失效，您可以尝试搜索"TensorRT 8.6.1 archive download"

2. 下载完成后，将TensorRT解压到项目根目录：
   - 解压后应该得到一个名为`TensorRT-8.6.1.6`或`TensorRT-8.6.1`的文件夹
   - 确保该文件夹位于与`1.webui运行.bat`相同的目录中
   - 文件夹内应包含`lib`子目录，其中有以下关键DLL文件：
     * nvinfer.dll
     * nvinfer_plugin.dll
     * nvonnxparser.dll
     * nvparsers.dll

3. 系统将自动检测TensorRT路径并设置环境变量

> **注意**：DLL文件是关键！最常见的TensorRT错误是`Could not find: nvinfer.dll. Is it on your PATH?`，这表示系统无法找到TensorRT的库文件。我们的启动脚本会尝试自动解决此问题。

### 启动方法

#### 方法一：使用批处理文件启动（推荐Windows用户）

1. 双击运行 `1.webui运行.bat`
2. 系统将自动设置TensorRT路径，安装Gradio依赖并启动界面
3. 启动成功后，将自动打开浏览器窗口，显示Gradio界面

#### 方法二：手动安装和启动

1. 手动设置TensorRT环境变量：
   ```
   set PATH=<项目路径>\TensorRT-8.6.1.6\lib;%PATH%
   ```

2. 确保DLL文件可被Python找到：
   ```
   copy <项目路径>\TensorRT-8.6.1.6\lib\nvinfer.dll <Python路径>\Lib\site-packages\tensorrt\
   ```

3. 安装Gradio库：
   ```
   pip install gradio>=3.50.2
   ```

4. 然后运行app.py脚本：
   ```
   python app.py
   ```

## 系统要求

### TensorRT版本要求

Ditto系统使用TensorRT加速推理，需要确保TensorRT版本与模型文件兼容：

- 必须使用TensorRT 8.6.1版本，这是模型创建时使用的版本
- 如果您使用其他版本的TensorRT，将出现"Failed due to an old deserialization call on a newer plan file"错误
- 您可以在界面的"系统信息"部分查看当前安装的TensorRT版本

### 其他依赖

- CUDA支持的NVIDIA GPU (推荐RTX系列)
- Python 3.8或更高版本
- 至少4GB的GPU内存
- 至少8GB的系统内存

## 使用指南

1. **上传音频文件**：点击"上传音频文件"区域，选择一个WAV格式的音频文件
2. **上传图片**：点击"上传图片"区域，选择一张包含人脸的图片
3. **高级设置**（可选）：
   - **使用固定随机种子**：勾选此选项可以使用固定的随机种子，确保结果的一致性
   - **随机种子值**：设置随机种子的值（默认为1024）
   - **淡入帧数**：设置视频开始时的淡入效果帧数（设为-1表示不使用）
   - **淡出帧数**：设置视频结束时的淡出效果帧数（设为-1表示不使用）
   - **模型设置**：可以自定义模型路径和配置文件路径
4. **检查系统信息**：点击"系统信息"查看您的环境配置，确保TensorRT版本兼容
5. **开始合成**：点击"开始合成"按钮，系统将开始处理
6. **查看结果**：处理完成后，合成的视频将显示在右侧区域，您可以播放或下载

## 示例文件

系统提供了示例文件路径供您参考：
- 音频示例：`./example/audio/sample1.wav`, `./example/audio/sample2.wav`
- 图像示例：`./example/images/sample1.jpg`, `./example/images/sample2.jpg`

您需要手动选择并上传这些文件进行测试。

## 注意事项

- 处理时间取决于您的计算机性能和输入音频的长度
- 图片应当是清晰的正面人脸照片，以获得最佳效果
- 音频应当是清晰的人声，背景噪音较少的录音效果更佳
- 处理完成的视频将临时保存在系统临时目录中，如需永久保存请下载
- 系统会自动寻找可用端口，如果默认的7860端口被占用

## 常见问题解答

1. **Q: 为什么视频合成失败？**  
   A: 请确保您的音频是WAV格式，图片中包含清晰的人脸，且模型路径设置正确。

2. **Q: 如何提高合成视频的质量？**  
   A: 使用高质量的输入图像和音频可以提高输出质量。此外，可以尝试调整高级设置中的参数。

3. **Q: 系统报错缺少依赖怎么办？**  
   A: 除Gradio外，系统还依赖于其他库。请确保您已安装requirements.txt中列出的所有依赖。

4. **Q: 出现"Could not find: nvinfer.dll"错误怎么办？**  
   A: 这表示Python无法找到TensorRT的DLL文件。解决方法：
   - 确保TensorRT-8.6.1.6文件夹在正确位置
   - 运行修改后的`1.webui运行.bat`，它会自动尝试复制DLL文件
   - 手动将DLL文件复制到Python的site-packages/tensorrt目录

5. **Q: 出现TensorRT版本错误怎么办？**  
   A: 这是因为您的TensorRT版本与模型创建时使用的版本不一致。请按照以下步骤解决：
   - 从NVIDIA官网下载TensorRT 8.6.1版本
   - 解压到项目根目录，确保目录名为`TensorRT-8.6.1.6`或`TensorRT-8.6.1`
   - 重新运行`1.webui运行.bat`启动脚本

6. **Q: 无法通过pip安装TensorRT 8.6.1怎么办？**  
   A: TensorRT 8.6.1无法通过pip直接安装，必须从NVIDIA官方网站下载安装包。请参考"TensorRT 8.6.1安装"部分的说明。

7. **Q: 端口错误怎么解决？**  
   A: 新版本会自动寻找可用端口。如果仍有问题，请确保没有其他程序占用相同端口，或者手动修改app.py中的端口设置。

8. **Q: 示例文件无法使用怎么办？**  
   A: 我们不再使用自动示例功能，请手动选择示例文件进行上传测试。

## 技术支持

如有任何问题或需要技术支持，请参考主项目的文档或提交issue。 