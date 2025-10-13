import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 数据导入服务
 * 对应后端的data_import.py
 */
export class DataImportService {
  /**
   * 上传文件
   * @param file 要上传的文件
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 上传结果
   */
  async uploadFile(file: File, sessionId?: string): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const formData = new FormData();
      formData.append('session_id', targetSessionId);
      formData.append('file', file);

      const response = await apiService.upload('/api/import/upload-file', formData);
      return response;
    } catch (error) {
      console.error('文件上传失败:', error);
      throw error;
    }
  }

  /**
   * 从数据库导入数据
   * @param dbType 数据库类型
   * @param host 数据库主机
   * @param port 数据库端口
   * @param database 数据库名称
   * @param table 表名
   * @param username 用户名（可选）
   * @param password 密码（可选）
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 导入结果
   */
  async importFromDatabase(
    dbType: string,
    host: string,
    port: number,
    database: string,
    table: string,
    username?: string,
    password?: string,
    sessionId?: string
  ): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const formData = new FormData();
      formData.append('session_id', targetSessionId);
      formData.append('db_type', dbType);
      formData.append('host', host);
      formData.append('port', port.toString());
      formData.append('database', database);
      formData.append('table', table);
      
      if (username) {
        formData.append('username', username);
      }
      
      if (password) {
        formData.append('password', password);
      }

      const response = await apiService.upload('/api/import/import-from-database', formData);
      return response;
    } catch (error) {
      console.error('数据库导入失败:', error);
      throw error;
    }
  }

  /**
   * 获取支持的文件格式
   * @returns string[] 支持的文件格式列表
   */
  getSupportedFileFormats(): string[] {
    return ['csv', 'excel', 'json', 'html', 'sqlite'];
  }
}

// 创建全局数据导入服务实例
export const dataImportService = new DataImportService();