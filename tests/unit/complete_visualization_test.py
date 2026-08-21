"""
完整的可视化模块测试
测试图表生成和验证功能
"""

import sys
import os
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_common_chart_generation():
    """测试通用图表生成"""
    try:
        # 生成测试数据
        X = np.random.rand(100, 2)
        y = np.random.rand(100)
        
        from backend.Models.visualization.upgrade.factory import VisualizationFactory
        
        factory = VisualizationFactory()
        
        # 测试散点图生成
        params = {
            "X": X,
            "y": y,
            "task_list": ["scatter"]
        }
        
        strategy = factory.create_visualization_strategy("no_model", "common", params)
        strategy.validate_params()
        
        # 生成静态图表
        static_charts = strategy.generate_static_charts()
        print(f"生成静态图表: {list(static_charts.keys())}")
        
        # 生成交互式图表
        interactive_charts = strategy.generate_interactive_charts()
        print(f"生成交互式图表: {list(interactive_charts.keys())}")
        
        print("✓ 散点图生成测试通过")
        return True
    except Exception as e:
        print(f"✗ 散点图生成测试失败: {e}")
        return False

def test_regression_strategies():
    """测试回归策略"""
    try:
        from backend.Models.visualization.upgrade.factory import VisualizationFactory
        from sklearn.linear_model import LinearRegression
        from sklearn.tree import DecisionTreeRegressor
        from sklearn.ensemble import RandomForestRegressor
        
        factory = VisualizationFactory()
        
        # 生成测试数据
        np.random.seed(42)
        X_train = np.random.rand(100, 5)
        y_train = np.random.rand(100)
        X_test = np.random.rand(20, 5)
        y_test = np.random.rand(20)
        
        # 测试线性回归
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        
        params = {
            "model": lr,
            "X_train": X_train,
            "y_train": y_train,
            "X_test": X_test,
            "y_test": y_test
        }
        
        strategy = factory.create_visualization_strategy("linearregression", "regression", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"线性回归生成静态图表: {list(static_charts.keys())}")
        
        # 测试决策树回归
        dt = DecisionTreeRegressor(random_state=42)
        dt.fit(X_train, y_train)
        
        params["model"] = dt
        strategy = factory.create_visualization_strategy("decisiontreeregressor", "regression", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"决策树回归生成静态图表: {list(static_charts.keys())}")
        
        # 测试随机森林回归
        rf = RandomForestRegressor(random_state=42)
        rf.fit(X_train, y_train)
        
        params["model"] = rf
        strategy = factory.create_visualization_strategy("randomforestregressor", "regression", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"随机森林回归生成静态图表: {list(static_charts.keys())}")
        
        print("✓ 回归策略测试通过")
        return True
    except Exception as e:
        print(f"✗ 回归策略测试失败: {e}")
        return False

def test_classification_strategies():
    """测试分类策略"""
    try:
        from backend.Models.visualization.upgrade.factory import VisualizationFactory
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.svm import SVC
        from sklearn.neighbors import KNeighborsClassifier
        
        factory = VisualizationFactory()
        
        # 生成测试数据
        np.random.seed(42)
        X_train = np.random.rand(100, 5)
        y_train = np.random.randint(0, 2, 100)  # 二分类
        X_test = np.random.rand(20, 5)
        y_test = np.random.randint(0, 2, 20)
        
        # 测试逻辑回归
        lr = LogisticRegression()
        lr.fit(X_train, y_train)
        
        params = {
            "model": lr,
            "X_train": X_train,
            "y_train": y_train,
            "X_test": X_test,
            "y_test": y_test
        }
        
        strategy = factory.create_visualization_strategy("logisticregression", "classification", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"逻辑回归生成静态图表: {list(static_charts.keys())}")
        
        # 测试决策树分类
        dt = DecisionTreeClassifier(random_state=42)
        dt.fit(X_train, y_train)
        
        params["model"] = dt
        strategy = factory.create_visualization_strategy("decisiontreeclassifier", "classification", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"决策树分类生成静态图表: {list(static_charts.keys())}")
        
        # 测试随机森林分类
        rf = RandomForestClassifier(random_state=42)
        rf.fit(X_train, y_train)
        
        params["model"] = rf
        strategy = factory.create_visualization_strategy("randomforestclassifier", "classification", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"随机森林分类生成静态图表: {list(static_charts.keys())}")
        
        # 测试SVM分类
        svm = SVC(probability=True)
        svm.fit(X_train, y_train)
        
        params["model"] = svm
        strategy = factory.create_visualization_strategy("svc", "classification", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"SVM分类生成静态图表: {list(static_charts.keys())}")
        
        # 测试KNN分类
        knn = KNeighborsClassifier()
        knn.fit(X_train, y_train)
        
        params["model"] = knn
        strategy = factory.create_visualization_strategy("kneighborsclassifier", "classification", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"KNN分类生成静态图表: {list(static_charts.keys())}")
        
        print("✓ 分类策略测试通过")
        return True
    except Exception as e:
        print(f"✗ 分类策略测试失败: {e}")
        return False

def test_clustering_strategies():
    """测试聚类策略"""
    try:
        from backend.Models.visualization.upgrade.factory import VisualizationFactory
        from sklearn.cluster import KMeans, MeanShift, AgglomerativeClustering
        
        factory = VisualizationFactory()
        
        # 生成测试数据
        np.random.seed(42)
        X = np.random.rand(100, 2)
        
        # 测试KMeans
        kmeans = KMeans(n_clusters=3, random_state=42)
        labels = kmeans.fit_predict(X)
        
        params = {
            "X": X,
            "model": kmeans,
            "labels": labels
        }
        
        strategy = factory.create_visualization_strategy("kmeans", "clustering", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"KMeans生成静态图表: {list(static_charts.keys())}")
        
        # 测试MeanShift
        meanshift = MeanShift()
        labels = meanshift.fit_predict(X)
        
        params["model"] = meanshift
        strategy = factory.create_visualization_strategy("meanshift", "clustering", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"MeanShift生成静态图表: {list(static_charts.keys())}")
        
        # 测试AgglomerativeClustering
        agg = AgglomerativeClustering(n_clusters=3)
        labels = agg.fit_predict(X)
        
        params["model"] = agg
        params["labels"] = labels
        strategy = factory.create_visualization_strategy("agglomerativeclustering", "clustering", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"AgglomerativeClustering生成静态图表: {list(static_charts.keys())}")
        
        print("✓ 聚类策略测试通过")
        return True
    except Exception as e:
        print(f"✗ 聚类策略测试失败: {e}")
        return False

def test_transformer_strategies():
    """测试变换器策略"""
    try:
        from backend.Models.visualization.upgrade.factory import VisualizationFactory
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        
        factory = VisualizationFactory()
        
        # 生成测试数据
        np.random.seed(42)
        X_train = np.random.rand(100, 5)
        
        # 测试PCA
        pca = PCA(n_components=2)
        pca.fit(X_train)
        
        params = {
            "model": pca,
            "X_train": X_train
        }
        
        strategy = factory.create_visualization_strategy("pca", "transformer", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"PCA生成静态图表: {list(static_charts.keys())}")
        
        # 测试StandardScaler
        scaler = StandardScaler()
        scaler.fit(X_train)
        
        params["model"] = scaler
        strategy = factory.create_visualization_strategy("standardscaler", "transformer", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"StandardScaler生成静态图表: {list(static_charts.keys())}")
        
        # 测试NoModel
        params = {
            "X_train": X_train,
            "values": [30, 20, 10],
            "labels": ["A", "B", "C"],
            "task_list": ["pie"]
        }
        
        strategy = factory.create_visualization_strategy("no_model", "transformer", params)
        strategy.validate_params()
        
        static_charts = strategy.generate_static_charts()
        print(f"NoModel生成静态图表: {list(static_charts.keys())}")
        
        print("✓ 变换器策略测试通过")
        return True
    except Exception as e:
        print(f"✗ 变换器策略测试失败: {e}")
        return False

def test_chart_selection():
    """测试图表选择功能"""
    try:
        from backend.Models.visualization.upgrade.strategy import VisualizationStrategySelector
        
        selector = VisualizationStrategySelector()
        
        # 测试分类任务图表选择
        classification_charts = selector.select_charts("classification", {})
        print(f"分类任务推荐图表: {classification_charts}")
        
        # 测试回归任务图表选择
        regression_charts = selector.select_charts("regression", {})
        print(f"回归任务推荐图表: {regression_charts}")
        
        # 测试聚类任务图表选择
        clustering_charts = selector.select_charts("clustering", {})
        print(f"聚类任务推荐图表: {clustering_charts}")
        
        print("✓ 图表选择功能测试通过")
        return True
    except Exception as e:
        print(f"✗ 图表选择功能测试失败: {e}")
        return False

def test_factory_model_support():
    """测试工厂模型支持功能"""
    try:
        from backend.Models.visualization.upgrade.factory import VisualizationFactory
        
        factory = VisualizationFactory()
        
        # 测试获取支持的模型
        supported_models = factory.get_supported_models()
        print(f"支持的模型数量: {len(supported_models)}")
        
        # 测试获取模型支持的任务
        lr_tasks = factory.get_model_supported_tasks("logisticregression")
        print(f"LogisticRegression支持的任务: {lr_tasks}")
        
        print("✓ 工厂模型支持功能测试通过")
        return True
    except Exception as e:
        print(f"✗ 工厂模型支持功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始完整测试DataVisualisationUpgrade模块...")
    print("=" * 50)
    
    tests = [
        test_factory_model_support,
        test_chart_selection,
        test_common_chart_generation,
        test_regression_strategies,
        test_classification_strategies,
        test_clustering_strategies,
        test_transformer_strategies
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！")
        return 0
    else:
        print("部分测试失败！")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)