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
   * 配置清理任务
   * @param interval 清理间隔（分钟）
   * @param max_age 最大保留时间（分钟）
   * @returns Promise<any> 配置结果
   */
  async configureCleanup(interval: number, max_age: number): Promise<any> {
    try {
      const response = await apiService.post(`/api/cleanup/configure?interval=${interval}&max_age=${max_age}`);
      return response;
    } catch (error) {
      console.error('配置清理任务失败:', error);
      throw error;
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
      return {
        files_removed: 0,
        space_freed: 0,
        sessions_closed: 0
      };
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

  /**
   * 格式化时间显示
   * @param minutes 分钟数
   * @returns string 格式化后的时间字符串
   */
  formatTime(minutes: number): string {
    if (minutes < 60) {
      return `${minutes} 分钟`;
    } else if (minutes < 24 * 60) {
      return `${(minutes / 60).toFixed(1)} 小时`;
    } else {
      return `${(minutes / (24 * 60)).toFixed(1)} 天`;
    }
  }
}

// 创建全局清理任务服务实例
export const cleanupTaskService = new CleanupTaskService();