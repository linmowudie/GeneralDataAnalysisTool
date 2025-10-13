import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 步骤锁服务
 * 对应后端的step_lock.py
 */
export class StepLockService {
  /**
   * 锁定指定的步骤
   * @param step 要锁定的步骤名称
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 锁定结果
   */
  async lockStep(
    step: string,
    sessionId?: string
  ): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const response = await apiService.post('/api/step/lock?session_id=' + targetSessionId + '&step=' + step);
      return response;
    } catch (error) {
      console.error('锁定步骤失败:', error);
      throw error;
    }
  }

  /**
   * 解锁指定的步骤
   * @param step 要解锁的步骤名称
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 解锁结果
   */
  async unlockStep(
    step: string,
    sessionId?: string
  ): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const response = await apiService.post('/api/step/unlock?session_id=' + targetSessionId + '&step=' + step);
      return response;
    } catch (error) {
      console.error('解锁步骤失败:', error);
      throw error;
    }
  }

  /**
   * 获取步骤状态
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 步骤状态信息
   */
  async getStepStatus(sessionId?: string): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const response = await apiService.get('/api/step/status', {
        params: { session_id: targetSessionId }
      });
      return response;
    } catch (error) {
      console.error('获取步骤状态失败:', error);
      // 返回默认状态作为备选
      return {
        completed_steps: [],
        locked_steps: []
      };
    }
  }

  /**
   * 同时锁定多个步骤
   * @param steps 要锁定的步骤名称列表
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 锁定结果
   */
  async lockMultipleSteps(
    steps: string[],
    sessionId?: string
  ): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      // 将数组参数转换为查询字符串参数
      const params = new URLSearchParams();
      params.append('session_id', targetSessionId);
      steps.forEach(step => params.append('steps', step));

      const response = await apiService.post('/api/step/lock-multiple?' + params.toString());
      return response;
    } catch (error) {
      console.error('锁定多个步骤失败:', error);
      throw error;
    }
  }

  /**
   * 检查步骤是否已锁定
   * @param step 要检查的步骤名称
   * @param lockedSteps 已锁定的步骤列表
   * @returns boolean 是否已锁定
   */
  isStepLocked(step: string, lockedSteps: string[]): boolean {
    return lockedSteps.includes(step);
  }

  /**
   * 获取所有有效的步骤名称
   * @returns string[] 有效的步骤名称列表
   */
  getValidSteps(): string[] {
    return ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report'];
  }

  /**
   * 获取步骤的中文名称
   * @returns Record<string, string> 步骤名称映射
   */
  getStepDisplayName(): Record<string, string> {
    return {
      'import': '数据导入',
      'preview': '数据预览',
      'cleaning': '数据清洗',
      'analysis': '数据分析',
      'visualization': '数据可视化',
      'report': '报告生成'
    };
  }
}

// 创建全局步骤锁服务实例
export const stepLockService = new StepLockService();