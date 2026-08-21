import { apiService } from './apiService';

/**
 * 模型提取服务
 * 对应后端的model_extractor.py
 */
export class ModelExtractorService {
  /**
   * 转移模型
   * @param modelName 模型名称（可选，如果不提供则转移最新的模型）
   * @returns Promise<any> 转移结果
   */
  async transferModel(modelName?: string): Promise<any> {
    try {
      let url = '/api/model/transfer';
      if (modelName) {
        url += '?model_name=' + modelName;
      }

      const response = await apiService.post(url);
      return response;
    } catch (error) {
      console.error('模型转移失败:', error);
      throw error;
    }
  }

  /**
   * 管理自动保存的模型
   * @param maxModels 自动保存目录中最大模型文件数量（默认为5）
   * @returns Promise<any> 管理结果
   */
  async manageModels(maxModels: number = 5): Promise<any> {
    try {
      const response = await apiService.post('/api/model/manage?max_models=' + maxModels);
      return response;
    } catch (error) {
      console.error('模型管理失败:', error);
      throw error;
    }
  }

  /**
   * 列出自动保存的模型
   * @returns Promise<any[]> 模型文件列表
   */
  async listAutoSavedModels(): Promise<any[]> {
    try {
      const response: any = await apiService.get('/api/model/list');
      return response.models || [];
    } catch (error) {
      console.error('获取模型列表失败:', error);
      return [];
    }
  }

  /**
   * 格式化模型文件大小显示
   * @param size 字节数
   * @returns string 格式化后的大小字符串
   */
  formatFileSize(size: number): string {
    if (size < 1024) {
      return `${size} B`;
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(2)} KB`;
    } else {
      return `${(size / (1024 * 1024)).toFixed(2)} MB`;
    }
  }

  /**
   * 格式化模型修改时间
   * @param timestamp 时间戳
   * @returns string 格式化后的时间字符串
   */
  formatModificationTime(timestamp: number): string {
    const date = new Date(timestamp * 1000); // 转换为毫秒
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}

// 创建全局模型提取服务实例
export const modelExtractorService = new ModelExtractorService();