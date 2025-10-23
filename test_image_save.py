import os
import matplotlib.pyplot as plt
import numpy as np

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 测试图片保存
def test_save_image():
    # 创建测试图像目录
    test_dir = os.path.join(PROJECT_ROOT, 'TestImages')
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    print(f"测试图像将保存到: {test_dir}")
    
    # 创建一个简单的图表
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)
    ax.set_title('测试图表')
    
    # 保存图表
    file_path = os.path.join(test_dir, 'test_save_image.png')
    fig.savefig(file_path, dpi=150, bbox_inches='tight')
    print(f"保存图表到: {file_path}")
    
    # 验证文件是否存在
    if os.path.exists(file_path):
        print(f"成功: 文件 {file_path} 已创建")
    else:
        print(f"失败: 文件 {file_path} 未创建")
    
    plt.close(fig)
    
    # 列出TestImages目录内容
    print("\nTestImages目录内容:")
    for file in os.listdir(test_dir):
        print(f"- {file}")

if __name__ == "__main__":
    test_save_image()