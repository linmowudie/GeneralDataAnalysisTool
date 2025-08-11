"""
save_sklearn_dataset.py
将 sklearn 内置数据集导出为 CSV 和 Excel 文件
"""

import pandas as pd
from sklearn import datasets
import os

# -------------------------------
# 配置区
# -------------------------------
DATASET_NAME = 'iris'  # 可选: 'iris', 'wine', 'breast_cancer', 'diabetes', 'boston' (旧版本), 'digits' 等
OUTPUT_DIR = 'Data'  # 输出目录

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# 加载数据集函数
# -------------------------------
def load_dataset(name: str) -> pd.DataFrame:
    """
    根据名称加载 sklearn 数据集并转换为 DataFrame
    """
    if name == 'iris':
        data = datasets.load_iris()
    elif name == 'wine':
        data = datasets.load_wine()
    elif name == 'breast_cancer':
        data = datasets.load_breast_cancer()
    elif name == 'diabetes':
        data = datasets.load_diabetes()
    elif name == 'digits':
        data = datasets.load_digits()
        # 数字图像数据较特殊，这里只取前100张展平为特征
        n_samples = 100
        flat_images = data.images[:n_samples].reshape(n_samples, -1)
        df = pd.DataFrame(flat_images)
        df['target'] = data.target[:n_samples]
        print(f"Digits 数据集较特殊，仅导出前 {n_samples} 个样本用于演示。")
        return df
    else:
        raise ValueError(f"不支持的数据集: {name}")

    # 构造 DataFrame
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = data.target

    # 如果有目标名称，也可以添加一列便于理解（可选）
    if hasattr(data, 'target_names'):
        df['target_name'] = data.target_names[data.target]

    return df

# -------------------------------
# 主程序
# -------------------------------
def main():
    try:
        print(f"正在加载 sklearn 数据集: {DATASET_NAME}")
        df = load_dataset(DATASET_NAME)

        print(f"数据集形状: {df.shape}")
        print(f"前几行数据:\n{df.head()}\n")

        # 保存为 CSV
        csv_file = os.path.join(OUTPUT_DIR, f"{DATASET_NAME}.csv")
        df.to_csv(csv_file, index=False)
        print(f"✅ 已保存为 CSV: {csv_file}")

        # 保存为 Excel（需要 openpyxl）
        excel_file = os.path.join(OUTPUT_DIR, f"{DATASET_NAME}.xlsx")
        df.to_excel(excel_file, index=False, sheet_name='Data')
        print(f"✅ 已保存为 Excel: {excel_file}")

        # 保存为 JSON
        json_file = os.path.join(OUTPUT_DIR, f"{DATASET_NAME}.json")
        df.to_json(json_file, orient='records', indent=2)
        print(f"✅ 已保存为 JSON: {json_file}")
        
        # 保存为 HTML
        html_file = os.path.join(OUTPUT_DIR, f"{DATASET_NAME}.html")
        df.to_html(html_file, index=False)
        print(f"✅ 已保存为 HTML: {html_file}")

        print(f"\n所有文件已保存到目录: {os.path.abspath(OUTPUT_DIR)}")

    except Exception as e:
        print(f"❌ 出错: {e}")

if __name__ == "__main__":
    main()