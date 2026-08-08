import React from 'react';
import type { ReactNode, ErrorInfo } from 'react';
import { Button, Result } from 'antd';
import { WarningOutlined } from '@ant-design/icons';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * 错误边界组件：捕获子组件渲染错误，防止白屏
 * 用法：包裹在路由模块或 App 最外层
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary 捕获错误:', error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <Result
          status="error"
          icon={<WarningOutlined style={{ color: '#c2ef4e' }} />}
          title="页面出错了"
          subTitle={this.state.error?.message || '组件渲染时发生未知错误'}
          extra={
            <Button type="primary" onClick={this.handleRetry}>
              重新加载
            </Button>
          }
        />
      );
    }
    return this.props.children;
  }
}
