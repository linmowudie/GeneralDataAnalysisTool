"""
运行common可视化测试
"""

import sys
import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 清理可能引起冲突的模块
modules_to_remove = [k for k in sys.modules.keys() if k.startswith('cv2') or k.startswith('ultralytics') or k.startswith('tests')]
for module in modules_to_remove:
    if module in sys.modules:
        del sys.modules[module]

def run_common_tests():
    """运行common可视化测试"""
    try:
        # 重新导入必要的模块
        import unittest
        
        # 直接导入测试模块
        test_module_path = os.path.join(PROJECT_ROOT, 'tests', 'unit', 'test_common_visualization.py')
        
        # 动态导入测试模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_common_visualization", test_module_path)
        if spec is not None:
            test_module = importlib.util.module_from_spec(spec)
            if spec.loader is not None:
                spec.loader.exec_module(test_module)
            
                # 获取测试类
                TestCommonVisualization = getattr(test_module, 'TestCommonVisualization')
                
                # 创建测试套件
                suite = unittest.TestLoader().loadTestsFromTestCase(TestCommonVisualization)
                
                # 运行测试
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)
                
                # 返回测试结果
                return result.wasSuccessful()
        else:
            print("无法加载测试模块")
            return False
        
    except Exception as e:
        print(f"运行测试时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_common_tests()
    sys.exit(0 if success else 1)