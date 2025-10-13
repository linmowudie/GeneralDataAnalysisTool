import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 数据分析服务
 * 对应后端的data_analysis.py
 */
export class DataAnalysisService {
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
      'nb': '朴素贝叶斯 - 用于分类任务'
    };
  }

  /**
   * 获取模型默认参数
   * @param modelType 模型类型
   * @returns Record<string, any> 默认参数配置
   */
  getDefaultParameters(modelType: string): Record<string, any> {
    // 根据不同模型类型返回默认参数配置
    const defaultParams: Record<string, Record<string, any>> = {
      'lr': {
        'random_state': 42,
        'is_split': true,
        'split_ratio': 0.8,
        'is_return_model_score': true
      },
      'rf': {
        'random_state': 42,
        'is_split': true,
        'split_ratio': 0.8,
        'model_params': {
          'n_estimators': 100
        }
      },
      'xgb': {
        'random_state': 42,
        'is_split': true,
        'split_ratio': 0.8,
        'model_params': {
          'n_estimators': 100,
          'learning_rate': 0.1
        }
      }
    };
    
    return defaultParams[modelType] || {
      'random_state': 42,
      'is_split': true,
      'split_ratio': 0.8
    };
  }
}

// 创建全局数据分析服务实例
export const dataAnalysisService = new DataAnalysisService();