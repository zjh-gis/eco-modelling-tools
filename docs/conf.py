# 导入Sphinx库
import os
import sys
import sphinx_rtd_theme
# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath('..'))

# 项目信息
project = '生态价值核算开源工具包'
author = 'zjh'
version = '1.0'
release = '1.0'

# 扩展
extensions = [
    'sphinx.ext.autodoc',      # 自动生成文档
    'sphinx.ext.viewcode',     # 在文档中显示源代码
    'sphinx.ext.todo',         # 添加待办事项
    'sphinx_rtd_theme',
]

# 主题设置
html_theme = 'sphinx_rtd_theme'  # 使用Read the Docs主题

# 自定义主题选项（可选）
html_theme_options = {
    'prev_next_buttons_location': 'both',  # 在顶部和底部显示上一篇和下一篇按钮
    'style_external_links': False,         # 不显示外部链接的图标
}

# 使用Read the Docs样式的Latex设置
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
}

# 扩展的配置选项（可选）
todo_include_todos = True  # 显示待办事项

# 自动文档生成设置
autodoc_mock_imports = []  # 需要模拟的导入，如果您的项目依赖于某些无法在文档构建环境中安装的包

# 源代码的路径
html_context = {
    'display_github': True,
    'github_user': 'zjh',
    'github_repo': 'https://gitee.com/zjhgis/eco-modelling_tools',
    'github_version': 'master/docs/source/',
}

# 扩展设置（可选）
# 例如，如果您使用sphinx.ext.autodoc扩展，您可以配置更多选项。

# 其他设置和配置项可以根据项目的需要进行添加和修改。

master_doc= '介绍'