import React, { useState } from 'react';
import { cleanupTaskService } from '../../services/cleanupTaskService';
import { apiService } from '../../services/apiService';

interface CleanupTaskModuleProps {
  activeStep: 'import' | 'preview' | 'cleaning' | 'analysis' | 'visualization' | 'report';
  onClearComplete?: () => void;
  onResetComplete?: () => void;
  addMessage?: (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;
}

const CleanupTaskModule: React.FC<CleanupTaskModuleProps> = ({ 
  activeStep, 
  onClearComplete,
  onResetComplete,
  addMessage 
}) => {
  const [isClearing, setIsClearing] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  // 清空当前及往后的步骤数据及结果
  const handleClear = async () => {
    if (isClearing) return;
    
    setIsClearing(true);
    try {
      const sessionId = apiService.getSessionId();
      if (!sessionId) {
        addMessage?.('未找到会话ID，无法清空数据', 'error');
        return;
      }

      // 根据当前步骤确定需要重置的步骤
      const steps = ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report'];
      const currentStepIndex = steps.indexOf(activeStep);
      
      if (currentStepIndex === -1) {
        addMessage?.('当前步骤无效', 'error');
        return;
      }

      // 重置当前及后续步骤
      for (let i = currentStepIndex; i < steps.length; i++) {
        try {
          await apiService.post('/api/import/reset-step', {
            session_id: sessionId,
            step: steps[i]
          });
        } catch (error) {
          console.error(`重置步骤 ${steps[i]} 失败:`, error);
          // 继续处理其他步骤，不中断整个过程
        }
      }

      // 调用后端清理任务服务清理临时文件
      try {
        await cleanupTaskService.runCleanup();
        addMessage?.(`已清空"${activeStep}"及后续步骤的数据和结果，并清理了临时文件`, 'success');
      } catch (error) {
        console.error('清理临时文件失败:', error);
        addMessage?.(`已清空"${activeStep}"及后续步骤的数据和结果，但清理临时文件失败`, 'warning');
      }
      
      onClearComplete?.();
    } catch (error) {
      console.error('清空操作失败:', error);
      addMessage?.('清空操作失败: ' + (error instanceof Error ? error.message : '未知错误'), 'error');
    } finally {
      setIsClearing(false);
    }
  };

  // 重置所有状态
  const handleReset = async () => {
    if (isResetting) return;
    
    setIsResetting(true);
    try {
      // 调用后端清理任务服务清理临时文件
      try {
        await cleanupTaskService.runCleanup();
        addMessage?.('已重置所有状态，并清理了临时文件', 'info');
      } catch (error) {
        console.error('清理临时文件失败:', error);
        addMessage?.('已重置所有状态，但清理临时文件失败', 'warning');
      }
      
      onResetComplete?.();
    } catch (error) {
      console.error('重置操作失败:', error);
      addMessage?.('重置操作失败: ' + (error instanceof Error ? error.message : '未知错误'), 'error');
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="cleanup-task-module">
      <div className="control-buttons">
        <button 
          className="control-btn clear-btn" 
          onClick={handleClear}
          disabled={isClearing}
        >
          {isClearing ? '清空中...' : '清空'}
        </button>
        <button 
          className="control-btn reset-btn" 
          onClick={handleReset}
          disabled={isResetting}
        >
          {isResetting ? '重置中...' : '重置'}
        </button>
      </div>
    </div>
  );
};

export default CleanupTaskModule;