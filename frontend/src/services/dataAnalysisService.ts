import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 模型配置接口定义
 */
export interface ModelInfo {
  class: string;
  type: string;
  init_params: string[];
  default_params: Record<string, unknown>;
}

export interface ModelConfig {
  [taskType: string]: {
    [modelName: string]: ModelInfo;
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
   * 获取模型配置（扁平化：{modelKey: ModelInfo}）
   */
  async getModelConfig(): Promise<Record<string, ModelInfo>> {
    try {
      if (this.modelConfig) {
        return this.flattenConfig(this.modelConfig);
      }
      const response: any = await apiService.get('/api/analysis/model-config');
      this.modelConfig = (response.config || {}) as ModelConfig;
      return this.flattenConfig(this.modelConfig);
    } catch (error) {
      console.error('获取模型配置失败:', error);
      return {};
    }
  }

  /**
   * 获取指定模型的元信息（init_params / default_params / type）
   */
  async getModelMeta(modelType: string): Promise<ModelInfo | null> {
    const config = await this.getModelConfig();
    return config[modelType] ?? null;
  }

  /**
   * 将嵌套配置扁平化为 {modelKey: ModelInfo}
   */
  private flattenConfig(config: ModelConfig): Record<string, ModelInfo> {
    const flat: Record<string, ModelInfo> = {};
    for (const models of Object.values(config)) {
      for (const [key, info] of Object.entries(models)) {
        flat[key] = info;
      }
    }
    return flat;
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
   * 获取模型类型的描述（从 model_config 的 type 字段推断）
   */
  getModelTypeDescriptions(): Record<string, string> {
    return {
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
}

// 创建全局数据分析服务实例
export const dataAnalysisService = new DataAnalysisService();