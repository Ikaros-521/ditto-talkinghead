@echo off
chcp 65001 > nul

echo 正在启动Ditto视频合成Gradio界面...
echo ================================================

REM 设置TensorRT路径
echo 设置TensorRT路径...
set CURRENT_DIR=%~dp0
set TENSORRT_DIR=

REM 检查多种可能的TensorRT路径
if exist "%CURRENT_DIR%TensorRT-8.6.1.6\lib" (
    set TENSORRT_DIR=%CURRENT_DIR%TensorRT-8.6.1.6
) else if exist "%CURRENT_DIR%\TensorRT-8.6.1.6\lib" (
    set TENSORRT_DIR=%CURRENT_DIR%\TensorRT-8.6.1.6
) else if exist "%CURRENT_DIR%TensorRT-8.6.1\lib" (
    set TENSORRT_DIR=%CURRENT_DIR%TensorRT-8.6.1
) else if exist "%CURRENT_DIR%\TensorRT-8.6.1\lib" (
    set TENSORRT_DIR=%CURRENT_DIR%\TensorRT-8.6.1
) else (
    echo 警告: 未找到TensorRT-8.6.1目录!
    echo 请确保TensorRT-8.6.1或TensorRT-8.6.1.6文件夹放置在程序根目录下。
    echo 您可以从NVIDIA官网下载TensorRT 8.6.1并解压到当前目录。
    echo 若要继续运行，请按任意键（可能会出现TensorRT错误）...
    pause
    goto CHECK_TENSORRT
)

REM 设置环境变量
set CUDA_DIR=%CURRENT_DIR%\Miniconda3\Lib\site-packages\torch\lib
set PATH=%TENSORRT_DIR%\lib;%CUDA_DIR%;%PATH%
set PYTHONPATH=%TENSORRT_DIR%\python;%PYTHONPATH%

REM 尝试复制DLL文件到Python目录以确保它们能被找到
echo 正在确保TensorRT DLL文件可被Python找到...
if not exist "Miniconda3\Lib\site-packages\tensorrt" (
    mkdir "Miniconda3\Lib\site-packages\tensorrt" 2>nul
)
if exist "%TENSORRT_DIR%\lib\nvinfer.dll" (
    copy /Y "%TENSORRT_DIR%\lib\nvinfer.dll" "Miniconda3\Lib\site-packages\tensorrt" >nul 2>&1
    copy /Y "%TENSORRT_DIR%\lib\nvinfer_plugin.dll" "Miniconda3\Lib\site-packages\tensorrt" >nul 2>&1
    copy /Y "%TENSORRT_DIR%\lib\nvonnxparser.dll" "Miniconda3\Lib\site-packages\tensorrt" >nul 2>&1
    copy /Y "%TENSORRT_DIR%\lib\nvparsers.dll" "Miniconda3\Lib\site-packages\tensorrt" >nul 2>&1
    echo TensorRT库文件已复制到Python目录
)

echo TensorRT路径已设置: %TENSORRT_DIR%\lib

echo ================================================

REM 启动Gradio界面
echo 启动Gradio界面...
echo 如果出现TensorRT错误，请查看GRADIO_README.md了解解决方案。
echo ================================================

Miniconda3\python.exe app.py

echo ================================================
echo 如果程序异常退出，请检查以下可能的原因:
echo 1. TensorRT版本不匹配 (推荐使用TensorRT 8.6.1)
echo 2. CUDA或GPU驱动程序问题
echo 3. 模型文件损坏或路径错误
echo ================================================

pause