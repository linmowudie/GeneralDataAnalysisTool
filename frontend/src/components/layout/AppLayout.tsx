import React from 'react';
import { Layout, Menu, Button, Tooltip, Popconfirm, Progress } from 'antd';
import {
  DashboardOutlined,
  ImportOutlined,
  TableOutlined,
  FilterOutlined,
  ExperimentOutlined,
  RobotOutlined,
  BarChartOutlined,
  FileTextOutlined,
  PlusOutlined,
  ApiOutlined,
} from '@ant-design/icons';
import { useLocation, useNavigate, Outlet } from 'react-router-dom';
import { useSession, STEP_ORDER } from '../../context/SessionContext';
import { LimeSquiggle } from '../common/Common';
import './AppLayout.css';

const { Sider, Header, Content } = Layout;

const NAV_ITEMS = [
  { key: '/', icon: <DashboardOutlined />, label: '工作台' },
  { key: '/import', icon: <ImportOutlined />, label: '数据导入', step: 'import' },
  { key: '/preview', icon: <TableOutlined />, label: '数据预览', step: 'preview' },
  { key: '/cleaning', icon: <FilterOutlined />, label: '数据清洗', step: 'cleaning' },
  { key: '/analysis', icon: <ExperimentOutlined />, label: '数据分析', step: 'analysis' },
  { key: '/agent', icon: <RobotOutlined />, label: 'Agent 自动分析' },
  { key: '/visualization', icon: <BarChartOutlined />, label: '数据可视化', step: 'visualization' },
  { key: '/report', icon: <FileTextOutlined />, label: '数据报表', step: 'report' },
];

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sessionId, stepStatus, newSession, ready } = useSession();

  const completedCount = STEP_ORDER.filter((s) => stepStatus.completed_steps.includes(s)).length;
  const progress = Math.round((completedCount / STEP_ORDER.length) * 100);

  return (
    <Layout className="df-layout">
      <Sider width={232} className="df-sider" theme="dark">
        <div className="df-brand">
          <div className="df-brand-mark">DF</div>
          <div className="df-brand-text">
            <div className="df-brand-name df-display">DataForge</div>
            <div className="df-micro df-brand-sub">通用数据分析工具</div>
          </div>
        </div>

        <Menu
          mode="inline"
          theme="dark"
          selectedKeys={[location.pathname]}
          onClick={({ key }) => navigate(key)}
          items={NAV_ITEMS.map((item) => ({
            key: item.key,
            icon: item.icon,
            label: (
              <span className="df-nav-label">
                {item.label}
                {item.step && stepStatus.completed_steps.includes(item.step) && (
                  <span className="df-nav-dot" aria-label="已完成" />
                )}
              </span>
            ),
          }))}
        />

        <div className="df-sider-footer">
          <LimeSquiggle />
          <div className="df-caption df-sider-tip">
            <ApiOutlined /> 后端五层架构 · v0.2.0
          </div>
        </div>
      </Sider>

      <Layout>
        <Header className="df-topbar">
          <div className="df-topbar-left">
            <span className="df-eyebrow">当前会话</span>
            <Tooltip title={sessionId || '会话初始化中…'}>
              <span className="df-pill df-code">
                {ready && sessionId ? sessionId.slice(0, 8) : '········'}
              </span>
            </Tooltip>
            <Popconfirm
              title="新建会话将清空当前数据，确定继续？"
              onConfirm={newSession}
              okText="确定"
              cancelText="取消"
            >
              <Button size="small" icon={<PlusOutlined />}>新建会话</Button>
            </Popconfirm>
          </div>
          <div className="df-topbar-right">
            <span className="df-caption">流程进度</span>
            <Progress
              percent={progress}
              size="small"
              style={{ width: 180 }}
              strokeColor="#c2ef4e"
              format={() => `${completedCount}/${STEP_ORDER.length}`}
            />
          </div>
        </Header>

        <Content className="df-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
