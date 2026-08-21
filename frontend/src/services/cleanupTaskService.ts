import { apiService } from './apiService';

/**
 * 清理任务服务
 * 对应后端的cleanup_task.py
 */
export class CleanupTaskService {
  /**
   * 立即执行清理任务
   * @returns Promise<any> 清理结果
   */
  async runCleanup(): Promise<any> {
    try {
      const response = await apiService.post('/api/cleanup/run', {});
      return response;
    } catch (error) {
      console.error('执行清理任务失败:', error);
      throw error;
    }
  }

  /**
   * 立即执行指定步骤的清理任务
   * @param step 步骤名称
   * @returns Promise<any> 清理结果
   */
  async runStepCleanup(step: string): Promise<any> {
    try {
      const response = await apiService.post(`/api/cleanup/run-step?step=${step}`, {});
      return response;
    } catch (error) {
      console.error(`执行步骤 ${step} 的清理任务失败:`, error);
      throw error;
    }
  }

  /**
   * 获取清理任务状态
   * @returns Promise<any> 清理任务状态信息
   */
  async getCleanupStatus(): Promise<any> {
    try {
      const response = await apiService.get('/api/cleanup/status');
      return response;
    } catch (error) {
      console.error('获取清理任务状态失败:', error);
      return {
        last_run: '未知',
        next_run: '未知',
        status: '无法获取'
      };
    }
  }

  /**
   * 获取清理统计信息
   * @returns Promise<any> 清理统计数据
   */
  async getCleanupStats(): Promise<any> {
    try {
      const response = await apiService.get('/api/cleanup/stats');
      return response;
    } catch (error) {
      console.error('获取清理统计信息失败:', error);
      throw error;
    }
  }

  /**
   * 格式化文件大小显示
   * @param bytes 字节数
   * @returns string 格式化后的大小字符串
   */
  formatFileSize(bytes: number): string {
    if (bytes < 1024) {
      return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    } else if (bytes < 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    } else {
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    }
  }
}

// 创建全局清理任务服务实例
export const cleanupTaskService = new CleanupTaskService();