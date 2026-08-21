import React from 'react';
import type { ReactNode } from 'react';
import { CheckCircleFilled, LockFilled } from '@ant-design/icons';
import { useSession } from '../../context/SessionContext';
import type { StepKey } from '../../context/SessionContext';
import './common.css';

/** 页面标题栏：eyebrow + 标题（可选青柠关键词高亮）+ 操作区 */
export const PageHeader: React.FC<{
  eyebrow?: string;
  title: ReactNode;
  extra?: ReactNode;
  description?: ReactNode;
}> = ({ eyebrow, title, extra, description }) => (
  <div className="df-page-header">
    <div className="df-page-header-left">
      {eyebrow && <div className="df-eyebrow">{eyebrow}</div>}
      <h1 className="df-page-title df-display">{title}</h1>
      {description && <p className="df-caption df-page-desc">{description}</p>}
    </div>
    {extra && <div className="df-page-header-extra">{extra}</div>}
  </div>
);

/** 统计卡片 */
export const StatCard: React.FC<{
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  accent?: 'lime' | 'pink' | 'violet';
}> = ({ label, value, hint, accent = 'violet' }) => (
  <div className={`df-card df-stat-card df-stat-${accent}`}>
    <div className="df-micro df-stat-label">{label}</div>
    <div className="df-display df-stat-value">{value}</div>
    {hint && <div className="df-caption">{hint}</div>}
  </div>
);

/** 步骤状态徽标：已完成 / 已锁定 / 待处理 */
export const StepStatusPill: React.FC<{ step: StepKey }> = ({ step }) => {
  const { isCompleted, isLocked } = useSession();
  if (isLocked(step)) {
    return (
      <span className="df-pill df-pill-locked">
        <LockFilled /> 已锁定
      </span>
    );
  }
  if (isCompleted(step)) {
    return (
      <span className="df-pill df-pill-done">
        <CheckCircleFilled /> 已完成
      </span>
    );
  }
  return <span className="df-pill">待处理</span>;
};

/** 青柠波浪分隔线（签名组件） */
export const LimeSquiggle: React.FC = () => (
  <svg
    className="df-squiggle"
    width="120"
    height="10"
    viewBox="0 0 120 10"
    fill="none"
    aria-hidden="true"
  >
    <path
      d="M1 6 Q 8 1, 15 6 T 29 6 T 43 6 T 57 6 T 71 6 T 85 6 T 99 6 T 113 6"
      stroke="#c2ef4e"
      strokeWidth="2.5"
      strokeLinecap="round"
    />
  </svg>
);
