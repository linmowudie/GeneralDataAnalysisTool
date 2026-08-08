import React from 'react';
import type { ReactNode } from 'react';
import { Alert } from 'antd';
import { useSession, type StepKey } from '../../context/SessionContext';

interface RouteGuardProps {
  children: ReactNode;
  /** 必须已完成的步骤（任一满足即可） */
  requireAnyOf?: StepKey[];
  /** 必须全部完成的步骤 */
  requireAllOf?: StepKey[];
}

/**
 * 路由守卫：基于步骤完成状态拦截访问
 *
 * 用法：
 *   <RouteGuard requireAnyOf={['import']}>
 *     <PreviewModule />
 *   </RouteGuard>
 */
const RouteGuard: React.FC<RouteGuardProps> = ({
  children,
  requireAnyOf,
  requireAllOf,
}) => {
  const { ready, isCompleted } = useSession();

  // 会话未就绪时不拦截（避免闪烁）
  if (!ready) return <>{children}</>;

  const completed = (step: StepKey) => isCompleted(step);

  // 检查 requireAllOf
  if (requireAllOf && requireAllOf.length > 0) {
    const allMet = requireAllOf.every(completed);
    if (!allMet) {
      const missing = requireAllOf.filter((s) => !completed(s));
      return (
        <Alert
          type="warning"
          showIcon
          message="前置步骤未完成"
          description={`请先完成：${missing.map((s) => STEP_LABELS[s] || s).join('、')}`}
          style={{ margin: 24 }}
        />
      );
    }
  }

  // 检查 requireAnyOf
  if (requireAnyOf && requireAnyOf.length > 0) {
    const anyMet = requireAnyOf.some(completed);
    if (!anyMet) {
      return (
        <Alert
          type="warning"
          showIcon
          message="前置步骤未完成"
          description={`请先完成以下任一步骤：${requireAnyOf.map((s) => STEP_LABELS[s] || s).join('、')}`}
          style={{ margin: 24 }}
        />
      );
    }
  }

  return <>{children}</>;
};

const STEP_LABELS: Record<string, string> = {
  import: '数据导入',
  preview: '数据预览',
  cleaning: '数据清洗',
  analysis: '数据分析',
  visualization: '数据可视化',
  report: '数据报表',
};

export default RouteGuard;
