# 简单测试脚本
print("测试项目结构...")

# 测试导入
print("\n测试导入模块...")
try:
    from src.project import get_all_projects, create_new_project
    from src.api import load_api_keys
    from src.logger import add_run_log
    print("✅ 所有模块导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")

# 测试项目管理
print("\n测试项目管理...")
try:
    projects = get_all_projects()
    print(f"✅ 当前项目数: {len(projects)}")
except Exception as e:
    print(f"❌ 项目管理测试失败: {e}")

print("\n测试完成！")
