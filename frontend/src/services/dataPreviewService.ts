import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 数据预览服务
 * 对应后端的data_preview.py
 */
export class DataPreviewService {
  /**
   * 获取数据预览
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 数据预览结果
   */
  async getDataPreview(sessionId?: string): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      // 直接将 session_id 作为查询参数传递
      const response = await apiService.get(`/api/preview/data-preview?session_id=${encodeURIComponent(targetSessionId)}`);
      return response;
    } catch (error) {
      console.error('获取数据预览失败:', error);
      throw error;
    }
  }

  /**
   * 获取数据集信息
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 数据集信息
   */
  async getDatasetInfo(sessionId?: string): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      // 直接将 session_id 作为查询参数传递
      const response = await apiService.get(`/api/preview/dataset-info?session_id=${encodeURIComponent(targetSessionId)}`);
      return response;
    } catch (error) {
      console.error('获取数据集信息失败:', error);
      throw error;
    }
  }

  /**
   * 格式化数据类型显示
   * @param dataType 数据类型
   * @returns string 格式化后的类型名称
   */
  formatDataType(dataType: string): string {
    const typeMap: Record<string, string> = {
      'int64': '整数',
      'float64': '浮点数',
      'object': '文本',
      'bool': '布尔值',
      'datetime64[ns]': '日期时间'
    };
    return typeMap[dataType] || dataType;
  }
}

// 创建全局数据预览服务实例
export const dataPreviewService = new DataPreviewService();