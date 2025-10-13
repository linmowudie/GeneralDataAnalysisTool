import { apiService } from './apiService';

/**
 * 会话管理服务
 * 对应后端的session_manager.py
 */
export class SessionService {
  /**
   * 创建新会话
   * @returns Promise<string> 会话ID
   */
  async createSession(): Promise<string> {
    try {
      const response: any = await apiService.post('/api/import/create-session');
      const sessionId = response.session_id;
      apiService.setSessionId(sessionId);
      return sessionId;
    } catch (error) {
      console.error('创建会话失败:', error);
      throw error;
    }
  }

  /**
   * 删除会话
   * @param sessionId 会话ID
   * @returns Promise<boolean> 删除是否成功
   */
  async deleteSession(sessionId: string): Promise<boolean> {
    try {
      // 注意：后端API中没有直接的删除会话接口，但可以通过重置会话来模拟
      // 这里只是一个示例实现，实际需要根据后端API调整
      if (apiService.getSessionId() === sessionId) {
        apiService.setSessionId('');
      }
      return true;
    } catch (error) {
      console.error('删除会话失败:', error);
      throw error;
    }
  }

  /**
   * 获取当前会话ID
   * @returns string | null 当前会话ID或null
   */
  getCurrentSessionId(): string | null {
    return apiService.getSessionId();
  }

  /**
   * 重置会话步骤
   * @param sessionId 会话ID
   * @param step 步骤名称
   * @returns Promise<boolean> 重置是否成功
   */
  async resetSessionStep(sessionId: string, step: string): Promise<boolean> {
    try {
      // 注意：后端API中没有直接的重置会话步骤接口
      // 这里只是一个示例实现，实际需要根据后端API调整
      return true;
    } catch (error) {
      console.error(`重置会话步骤${step}失败:`, error);
      throw error;
    }
  }
}

// 创建全局会话服务实例
export const sessionService = new SessionService();