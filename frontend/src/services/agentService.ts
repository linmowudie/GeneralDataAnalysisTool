import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * Agent 自动分析服务
 * 对应后端 /api/agent/* 五端点
 */

export interface AgentProfile {
  n_rows: number;
  n_cols: number;
  columns: Array<{ name: string; dtype: string; n_unique?: number; missing?: number }>;
  task_type?: string;
  target_col?: string | null;
  [key: string]: any;
}

export interface PlanCandidate {
  model_type: string;
  task_type: string;
  priority: number;
  reason?: string;
  [key: string]: any;
}

export interface EvaluationReport {
  status: string;
  score: number | null;
  metrics_evaluated: Record<string, number>;
  suggestion: string;
  next_action: string;
}

export interface AttemptRecord {
  model_type: string;
  task_type: string;
  metrics: Record<string, number>;
  evaluation?: EvaluationReport | null;
  error?: string | null;
}

export interface AgentDecision {
  session_id: string;
  profile?: AgentProfile | null;
  attempts: AttemptRecord[];
  best?: AttemptRecord | null;
  finished_at?: string;
}

export class AgentService {
  private resolveSession(sessionId?: string): string {
    const sid = sessionId || sessionService.getCurrentSessionId();
    if (!sid) throw new Error('没有可用的会话ID，请先创建会话');
    return sid;
  }

  /** 数据画像 */
  async dataProfile(sessionId?: string, targetCol?: string): Promise<AgentProfile> {
    const sid = this.resolveSession(sessionId);
    const res: any = await apiService.get('/api/agent/data-profile', {
      session_id: sid,
      ...(targetCol ? { target_col: targetCol } : {}),
    });
    return res.profile;
  }

  /** 推荐分析方法 */
  async recommendMethods(sessionId?: string, targetCol?: string): Promise<PlanCandidate[]> {
    const sid = this.resolveSession(sessionId);
    const url = `/api/agent/recommend-methods?session_id=${encodeURIComponent(sid)}` +
      (targetCol ? `&target_col=${encodeURIComponent(targetCol)}` : '');
    const res: any = await apiService.post(url);
    return res.candidates || [];
  }

  /** 评估当前分析结果 */
  async evaluate(sessionId?: string): Promise<EvaluationReport> {
    const sid = this.resolveSession(sessionId);
    const res: any = await apiService.post(`/api/agent/evaluate?session_id=${encodeURIComponent(sid)}`);
    return res.evaluation;
  }

  /** 自动分析闭环 */
  async autoAnalyze(
    sessionId?: string,
    options?: { maxCandidates?: number; targetCol?: string; timeoutSec?: number }
  ): Promise<AgentDecision> {
    const sid = this.resolveSession(sessionId);
    const params = new URLSearchParams({ session_id: sid });
    if (options?.maxCandidates) params.set('max_candidates', String(options.maxCandidates));
    if (options?.targetCol) params.set('target_col', options.targetCol);
    if (options?.timeoutSec) params.set('timeout_sec', String(options.timeoutSec));
    const res: any = await apiService.post(`/api/agent/auto-analyze?${params.toString()}`);
    return res.decision;
  }

  /** 查询最近决策 */
  async getDecision(sessionId?: string): Promise<AgentDecision | null> {
    const sid = this.resolveSession(sessionId);
    const res: any = await apiService.get('/api/agent/decision', { session_id: sid });
    return res.decision || null;
  }
}

export const agentService = new AgentService();
