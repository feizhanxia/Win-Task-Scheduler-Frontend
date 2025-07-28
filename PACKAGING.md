# Windows Task Scheduler Frontend

这是一个基于 Streamlit 的 Windows 任务计划程序前端应用。

## 打包说明

### 问题原因
你之前遇到的问题是因为 Streamlit 应用不能像普通的 Python 脚本一样直接打包执行。Streamlit 需要通过 `streamlit run` 命令来启动服务器，所以需要特殊的打包方式。

### 正确的打包方法

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **Windows 用户运行打包脚本**：
   ```cmd
   build.bat
   ```

3. **macOS/Linux 用户运行打包脚本**：
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

4. **手动打包（推荐）**：
   ```bash
   # 安装 PyInstaller
   pip install pyinstaller
   
   # 使用 spec 文件打包
   pyinstaller TaskScheduler.spec --clean --noconfirm
   ```

### 运行打包后的应用

打包完成后，可执行文件会在 `dist` 文件夹中：
- Windows: `dist/TaskScheduler.exe`
- macOS/Linux: `dist/TaskScheduler`

运行可执行文件后：
1. 程序会自动启动 Streamlit 服务器
2. 在浏览器中打开 http://localhost:8501
3. 使用 Ctrl+C 停止应用

### 重要变更

1. **新增 `main.py`**: 作为应用的入口点，负责正确启动 Streamlit 服务器
2. **新增 `TaskScheduler.spec`**: PyInstaller 配置文件，包含所有必要的依赖和数据文件
3. **更新 `requirements.txt`**: 添加了 PyInstaller 依赖

### 技术细节

- 使用 `subprocess` 调用 `streamlit run` 命令而不是直接导入 Streamlit 模块
- 在 `.spec` 文件中包含所有 Streamlit 相关的隐藏导入
- 确保模板文件和其他资源文件被正确打包
- 设置合适的 Streamlit 服务器参数以避免 CORS 警告

## 开发模式运行

如果要在开发环境中运行：
```bash
streamlit run app.py
```

或者：
```bash
python main.py
```
