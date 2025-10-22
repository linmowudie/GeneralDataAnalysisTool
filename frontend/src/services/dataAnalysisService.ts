import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 模型配置接口定义
 */
export interface ModelConfig {
  [modelType: string]: {
    [modelName: string]: {
      class: string;
      type: string;
      init_params: string[];
      default_params: Record<string, any>;
    };
  };
}

/**
 * 数据分析服务
 * 对应后端的data_analysis.py
 */
export class DataAnalysisService {
  private modelConfig: ModelConfig | null = null;

  /**
   * 运行数据分析
   * @param modelType 模型类型
   * @param parameters 分析参数
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 分析结果
   */
  async runAnalysis(
    modelType: string,
    parameters: Record<string, any> = {},
    sessionId?: string
  ): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const formData = new FormData();
      formData.append('session_id', targetSessionId);
      formData.append('model_type', modelType);
      formData.append('parameters', JSON.stringify(parameters));

      const response = await apiService.upload('/api/analysis/run-analysis', formData);
      return response;
    } catch (error) {
      console.error('数据分析失败:', error);
      throw error;
    }
  }

  /**
   * 获取可用的分析模型
   * @returns Promise<string[]> 模型列表
   */
  async getAvailableModels(): Promise<string[]> {
    try {
      const response: any = await apiService.get('/api/analysis/available-models');
      return response.models || [];
    } catch (error) {
      console.error('获取可用模型失败:', error);
      throw error;
    }
  }

  /**
   * 获取模型配置
   * @returns Promise<ModelConfig> 模型配置
   */
  async getModelConfig(): Promise<ModelConfig> {
    try {
      // 如果已经获取过配置，直接返回缓存
      if (this.modelConfig) {
        return this.modelConfig;
      }
      
      // 从后端获取模型配置
      const response: any = await apiService.get('/api/analysis/model-config');
      this.modelConfig = response.config || {};
      return this.modelConfig || {};
    } catch (error) {
      console.error('获取模型配置失败:', error);
      // 如果API调用失败，返回默认配置
      return this.getDefaultModelConfig();
    }
  }

  /**
   * 获取当前会话的数据列信息
   * @param sessionId 会话ID
   * @returns Promise<string[]> 列名列表
   */
  async getDataColumns(sessionId?: string): Promise<string[]> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      const response: any = await apiService.get(`/api/analysis/data-columns/${targetSessionId}`);
      return response.columns || [];
    } catch (error) {
      console.error('获取数据列信息失败:', error);
      return [];
    }
  }

  /**
   * 获取模型类型的描述
   * @returns Record<string, string> 模型名称和描述的映射
   */
  getModelTypeDescriptions(): Record<string, string> {
    // 这是一个示例映射，实际应该从后端获取或配置文件中读取
    return {
      'lr': '线性回归模型 - 用于回归任务',
      'rf': '随机森林模型 - 用于分类和回归任务',
      'xgb': 'XGBoost模型 - 强大的梯度提升模型',
      'svm': '支持向量机 - 用于分类和回归任务',
      'dt': '决策树 - 直观的分类和回归模型',
      'knn': 'K近邻算法 - 基于距离的分类方法',
      'nb': '朴素贝叶斯 - 用于分类任务',
      'linearregression': '线性回归 - 基本回归算法',
      'ridge': '岭回归 - 带L2正则化的线性回归',
      'lasso': 'Lasso回归 - 带L1正则化的线性回归',
      'logisticregression': '逻辑回归 - 用于分类任务',
      'decisiontreeclassifier': '决策树分类器',
      'kneighborsclassifier': 'K近邻分类器',
      'svc': '支持向量分类器',
      'kmeans': 'K均值聚类',
      'meanshift': '均值漂移聚类',
      'dbscan': 'DBSCAN聚类',
      'pca': '主成分分析 - 降维方法',
      'standardscaler': '标准化缩放器',
      'minmaxscaler': '最小-最大缩放器',
      'tsne': 't-SNE - 非线性降维',
      'apriori': 'Apriori算法 - 关联规则挖掘',
      'associationrules': '关联规则生成器'
    };
  }

  /**
   * 获取模型默认参数
   * @param modelType 模型类型
   * @returns Record<string, any> 默认参数配置
   */
  getDefaultParameters(modelType: string): Record<string, any> {
    // 基础默认参数
    const baseParams = {
      'random_state': 42,
      'is_split': true,
      'split_ratio': 0.8,
      'is_return_model_score': true,
      'model_params': {}
    };
    
    // 特殊模型的参数处理
    switch (modelType) {
      case 'rf':
        baseParams.model_params = { n_estimators: 100 };
        break;
      case 'xgb':
        baseParams.model_params = { n_estimators: 100, learning_rate: 0.1 };
        break;
      case 'svm':
      case 'svc':
        baseParams.model_params = { C: 1.0, kernel: 'rbf' };
        break;
      case 'decisiontreeclassifier':
        baseParams.model_params = { max_depth: null, min_samples_split: 2 };
        break;
      case 'kmeans':
        baseParams.model_params = { n_clusters: 3 };
        break;
      default:
        break;
    }
    
    return baseParams;
  }

  /**
   * 获取默认模型配置（当API调用失败时使用）
   * @returns ModelConfig 默认模型配置
   */
  private getDefaultModelConfig(): ModelConfig {
    // 这里可以添加一个简化版的默认配置，基于已知的model_config.json结构
    return {
      'regression': {
        'linearregression': {
          'class': 'LinearRegression',
          'type': 'regression',
          'init_params': ['fit_intercept'],
          'default_params': { 'fit_intercept': true }
        }
      },
      'classification': {
        'logisticregression': {
          'class': 'LogisticRegression',
          'type': 'classification',
          'init_params': ['C', 'max_iter'],
          'default_params': { 'C': 1.0, 'max_iter': 1000 }
        }
      }
    };
  }
}

// 创建全局数据分析服务实例
export const dataAnalysisService = new DataAnalysisService();