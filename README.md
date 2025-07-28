# Windows Task Scheduler Frontend

这是一个基于 Streamlit 的 Windows 任务计划程序前端管理界面。

## 功能特性
- 列出 `\PyTasks` 命名空间下的任务
- 创建、编辑、删除、启用/禁用任务
- 查看日志和立即运行任务

## 快速开始

### 方法1：使用批处理脚本（推荐）
1. **双击运行**：
   - `启动任务计划程序.bat` （中文界面）
   - `run.bat` （英文界面）

2. **脚本功能**：
   - 自动检查 Python 是否安装
   - 自动安装缺失的依赖包
   - 自动检查端口占用
   - 自动打开浏览器
   - 启动 Streamlit 服务器

### 方法2：手动运行
1. **安装 Python 3.8+ 和 pip**

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用**：
   ```bash
   streamlit run app.py
   ```

4. **访问应用**：
   打开浏览器访问 http://localhost:8501

## Packaging
To build a standalone EXE with PyInstaller:
```bash
pip install pyinstaller
# include the templates directory so the XML template is bundled
# copy Streamlit's metadata so importlib.metadata works when running the EXE
pyinstaller --onefile app.py \
  --add-data "templates;templates" \
  --copy-metadata streamlit
```
The resulting executable will be in the `dist` directory with the
`templates` folder packaged alongside the binary.

## Example XML Template
See `templates/task_template.xml` for the base schedule task template used for creation.
