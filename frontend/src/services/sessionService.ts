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
      const data: any = await apiService.post('/api/session/create');
      const sessionId = data.session_id;
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
      const formData = new FormData();
      formData.append('session_id', sessionId);
      await apiService.upload('/api/session/end', formData);
      
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
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('step', step);
      await apiService.upload('/api/session/reset-step', formData);
      return true;
    } catch (error) {
      console.error(`重置会话步骤${step}失败:`, error);
      throw error;
    }
  }
  
  /**
   * 重置会话中的所有数据
   * @param sessionId 会话ID
   * @returns Promise<boolean> 重置是否成功
   */
  async resetAllSessionData(sessionId: string): Promise<boolean> {
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      await apiService.upload('/api/session/reset-all', formData);
      return true;
    } catch (error) {
      console.error('重置会话所有数据失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取会话步骤状态
   * @param sessionId 会话ID
   * @returns Promise<any> 步骤状态信息
   */
  async getSessionStepStatus(sessionId: string): Promise<any> {
    try {
      const response = await apiService.get(`/api/session/step-status?session_id=${encodeURIComponent(sessionId)}`);
      return response;
    } catch (error) {
      console.error('获取会话步骤状态失败:', error);
      throw error;
    }
  }
}

// 创建全局会话服务实例
export const sessionService = new SessionService();