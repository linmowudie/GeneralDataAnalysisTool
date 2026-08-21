import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { message } from 'antd';
import { sessionService } from '../services/sessionService';
import { apiService } from '../services/apiService';

/**
 * SessionContext：全局会话与步骤状态管理
 * - 自动创建/恢复会话（localStorage 持久化）
 * - 步骤状态（completed/locked）供导航与流水线展示
 */

export const STEP_ORDER = ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report'] as const;
export type StepKey = typeof STEP_ORDER[number];

export const STEP_LABELS: Record<StepKey, string> = {
  import: '数据导入',
  preview: '数据预览',
  cleaning: '数据清洗',
  analysis: '数据分析',
  visualization: '数据可视化',
  report: '数据报表',
};

interface StepStatus {
  completed_steps: string[];
  locked_steps: string[];
}

interface SessionContextType {
  sessionId: string | null;
  ready: boolean;
  stepStatus: StepStatus;
  /** 刷新步骤状态（执行操作后调用） */
  refreshStatus: () => Promise<void>;
  /** 新建会话并重置状态 */
  newSession: () => Promise<void>;
  isCompleted: (step: StepKey) => boolean;
  isLocked: (step: StepKey) => boolean;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

const STORAGE_KEY = 'dataforge_session_id';

export const SessionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [stepStatus, setStepStatus] = useState<StepStatus>({
    completed_steps: [],
    locked_steps: [],
  });

  const refreshStatus = useCallback(async () => {
    const sid = apiService.getSessionId();
    if (!sid) return;
    try {
      const res: any = await sessionService.getSessionStepStatus(sid);
      setStepStatus({
        completed_steps: res?.status?.completed_steps || [],
        locked_steps: res?.status?.locked_steps || [],
      });
    } catch {
      // 会话可能已过期，静默处理
    }
  }, []);

  const createSession = useCallback(async () => {
    try {
      const sid = await sessionService.createSession();
      localStorage.setItem(STORAGE_KEY, sid);
      setSessionId(sid);
      setStepStatus({ completed_steps: [], locked_steps: [] });
    } catch (e: any) {
      message.error(`创建会话失败：${e?.message || e}`);
    }
  }, []);

  // 启动：恢复或新建会话
  useEffect(() => {
    (async () => {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        apiService.setSessionId(stored);
        setSessionId(stored);
        // 验证会话有效性
        try {
          const res: any = await sessionService.getSessionStepStatus(stored);
          setStepStatus({
            completed_steps: res?.status?.completed_steps || [],
            locked_steps: res?.status?.locked_steps || [],
          });
        } catch {
          await createSession();
        }
      } else {
        await createSession();
      }
      setReady(true);
    })();
  }, [createSession]);

  const newSession = useCallback(async () => {
    const old = apiService.getSessionId();
    if (old) {
      sessionService.deleteSession(old).catch(() => undefined);
    }
    localStorage.removeItem(STORAGE_KEY);
    await createSession();
  }, [createSession]);

  const isCompleted = useCallback(
    (step: StepKey) => stepStatus.completed_steps.includes(step),
    [stepStatus]
  );

  const isLocked = useCallback(
    (step: StepKey) => stepStatus.locked_steps.includes(step),
    [stepStatus]
  );

  return (
    <SessionContext.Provider
      value={{ sessionId, ready, stepStatus, refreshStatus, newSession, isCompleted, isLocked }}
    >
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession 必须在 SessionProvider 内使用');
  return ctx;
};
