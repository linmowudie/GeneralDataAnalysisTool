import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 数据清洗服务
 * 对应后端的data_cleaning.py
 */
export class DataCleaningService {
  /**
   * 执行数据清洗
   * @param mode 清洗模式
   * @param isCustom 是否为自定义清洗
   * @param parameters 清洗参数
   * @param targetCol 目标列（可选）
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 清洗结果
   */
  async cleanData(
    mode: string,
    isCustom: boolean = false,
    parameters: Record<string, any> = {},
    targetCol?: string,
    sessionId?: string
  ): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const formData = new FormData();
      formData.append('session_id', targetSessionId);
      formData.append('mode', mode);
      formData.append('is_custom', isCustom.toString());
      formData.append('parameters', JSON.stringify(parameters));
      
      if (targetCol) {
        formData.append('target_col', targetCol);
      }

      const response = await apiService.upload('/api/cleaning/clean-data', formData);
      return response;
    } catch (error) {
      console.error('数据清洗失败:', error);
      throw error;
    }
  }

  /**
   * 获取可用的清洗模式
   * @returns Promise<string[]> 清洗模式列表
   */
  async getCleaningModes(): Promise<string[]> {
    try {
      const response: any = await apiService.get('/api/cleaning/cleaning-modes');
      return response.modes || [];
    } catch (error) {
      console.error('获取清洗模式失败:', error);
      // 返回默认模式列表作为备选
      return ['standard', 'strict', 'relaxed', 'custom'];
    }
  }

  /**
   * 获取各清洗模式的描述
   * @returns Record<string, string> 模式名称和描述的映射
   */
  getCleaningModeDescriptions(): Record<string, string> {
    return {
      'standard': '标准清洗模式，适用于大多数数据集',
      'strict': '严格清洗模式，对数据质量要求较高',
      'relaxed': '宽松清洗模式，保留尽可能多的数据',
      'custom': '自定义清洗模式，根据指定参数进行清洗'
    };
  }
}

// 创建全局数据清洗服务实例
export const dataCleaningService = new DataCleaningService();