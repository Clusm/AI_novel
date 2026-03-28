"""
pytest 配置和 fixtures
"""

import pytest
import os
import sys
import tempfile
import shutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_workspace():
    """创建临时工作空间"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_project(temp_workspace):
    """创建临时项目"""
    from src.project import create_new_project
    
    project_name = "test_project"
    project_path = os.path.join(temp_workspace, "projects", project_name)
    os.makedirs(project_path, exist_ok=True)
    
    # 创建必要的目录
    for subdir in ["chapters", "summaries", "canon", "logs"]:
        os.makedirs(os.path.join(project_path, subdir), exist_ok=True)
    
    # 创建配置文件
    import json
    config = {
        "name": project_name,
        "writing_style": "standard",
        "created_at": "2024-01-01",
    }
    with open(os.path.join(project_path, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f)
    
    yield project_name, project_path


@pytest.fixture
def mock_api_keys():
    """模拟 API Keys"""
    return {
        "DEEPSEEK_API_KEY": "test-deepseek-key",
        "DASHSCOPE_API_KEY": "test-dashscope-key",
        "MOONSHOT_API_KEY": "test-moonshot-key",
        "ROUTE_PROFILE": "speed",
        "WRITER_MODEL": "auto",
    }


@pytest.fixture
def sample_outline():
    """示例大纲"""
    return """
# 故事大纲

## 背景
这是一个修仙世界，主角林风是一个普通少年。

## 主线
1. 林风意外获得神秘功法
2. 进入宗门修炼
3. 历经磨难，不断突破
4. 最终成为一代强者

## 人物
- 林风：主角，性格坚韧
- 苏瑶：女主，天赋异禀
- 陈长老：反派，心机深沉
"""


@pytest.fixture
def sample_chapter():
    """示例章节"""
    return """
林风站在山顶，望着远处的云海，心中感慨万千。

三个月前，他还只是一个普通的山村少年，每天的生活就是砍柴、挑水、照顾生病的母亲。

但那块神秘的玉佩改变了一切。

那天，他在山洞中避雨，无意中发现了这块散发着淡淡光芒的玉佩。当他触碰玉佩的瞬间，一股庞大的信息涌入脑海——那是一部名为《太玄经》的修炼功法。

从那天起，他的命运彻底改变了。

"林风，你在想什么？"

一个清脆的声音打断了他的思绪。林风转过头，看到一个身穿白衣的少女正向他走来。

是苏瑶。

"没什么，只是觉得这一切像做梦一样。"林风微微一笑。

苏瑶走到他身边，也望向远方的云海："我理解你的感受。当初我刚进入宗门时，也是这样。不过，既然选择了这条路，就要坚定地走下去。"

林风点了点头。是啊，既然选择了这条路，就要坚定地走下去。

无论前方有多少艰难险阻，他都不会退缩。
"""
