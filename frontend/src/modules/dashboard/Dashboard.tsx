import React from 'react';
import './Dashboard.css';

interface DashboardProps {
  onTabChange: (tab: 'dashboard' | 'analysis' | 'visualization') => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onTabChange }) => {
  // 模拟数据
  const recentProjects = [
    { id: 1, name: '乳腺癌数据分析', date: '2024-05-20', status: '已完成' },
    { id: 2, name: '房价预测模型', date: '2024-05-18', status: '进行中' },
    { id: 3, name: '糖尿病数据集清洗', date: '2024-05-15', status: '已完成' },
  ];

  const dataStats = {
    totalProjects: 15,
    completedProjects: 12,
    pendingProjects: 3,
    totalDataSize: '2.5GB',
  };

  const notifications = [
    { id: 1, message: '新的数据清洗算法已上线', time: '10分钟前', isRead: false },
    { id: 2, message: '系统将在今晚23:00-24:00进行维护', time: '2小时前', isRead: false },
    { id: 3, message: '您的乳腺癌数据分析已完成', time: '昨天', isRead: true },
  ];

  const quickActions = [
    { id: 1, name: '新建分析', icon: '+', color: 'primary' },
    { id: 2, name: '导入数据', icon: '↥', color: 'success' },
    { id: 3, name: '数据清洗', icon: '🧹', color: 'warning' },
    { id: 4, name: '模型训练', icon: '⚙️', color: 'error' },
  ];

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>通用数据分析工具</h2>
        <div className="dashboard-tabs">
          <button className="tab-button active" onClick={() => onTabChange('dashboard')}>仪表盘</button>
          <button className="tab-button" onClick={() => onTabChange('analysis')}>数据分析</button>
          <button className="tab-button" onClick={() => onTabChange('visualization')}>绘图</button>
        </div>
      </div>

      {/* 仪表盘内容区域 - 卡片式布局 */}
      <div className="dashboard-dashboard-content">
        {/* 数据统计卡片 */}
        <div className="dashboard-stats-grid">
          <div className="dashboard-stat-card">
            <h3>总项目数</h3>
            <p className="dashboard-stat-value">{dataStats.totalProjects}</p>
            <p className="dashboard-stat-description">所有分析项目</p>
          </div>
          <div className="dashboard-stat-card">
            <h3>已完成项目</h3>
            <p className="dashboard-stat-value">{dataStats.completedProjects}</p>
            <p className="dashboard-stat-description">成功完成的项目</p>
          </div>
          <div className="dashboard-stat-card">
            <h3>进行中项目</h3>
            <p className="dashboard-stat-value">{dataStats.pendingProjects}</p>
            <p className="dashboard-stat-description">正在处理的项目</p>
          </div>
          <div className="dashboard-stat-card">
            <h3>数据总量</h3>
            <p className="dashboard-stat-value">{dataStats.totalDataSize}</p>
            <p className="dashboard-stat-description">已处理数据</p>
          </div>
        </div>

        {/* 主要内容区域 - 左右布局 */}
        <div className="dashboard-main-grid">
          {/* 左侧区域 */}
          <div className="dashboard-left-section">
            {/* 最近项目卡片 */}
            <div className="dashboard-card">
              <div className="dashboard-card-header">
                <h3>最近项目</h3>
                <button className="dashboard-card-action">查看全部</button>
              </div>
              <div className="dashboard-card-body">
                <table className="dashboard-project-table">
                  <thead>
                    <tr>
                      <th>项目名称</th>
                      <th>日期</th>
                      <th>状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentProjects.map(project => (
                      <tr key={project.id}>
                        <td>{project.name}</td>
                        <td>{project.date}</td>
                        <td>
                          <span className={`dashboard-status-badge ${project.status === '已完成' ? 'completed' : 'pending'}`}>
                            {project.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* 常用工具卡片 */}
            <div className="dashboard-card">
              <div className="dashboard-card-header">
                <h3>快速操作</h3>
              </div>
              <div className="dashboard-card-body">
                <div className="dashboard-quick-actions">
                  {quickActions.map(action => (
                    <button key={action.id} className={`dashboard-quick-action-btn ${action.color}`}>
                      <span className="dashboard-action-icon">{action.icon}</span>
                      <span>{action.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 右侧区域 */}
          <div className="dashboard-right-section">
            {/* 可视化卡片 */}
            <div className="dashboard-card">
              <div className="dashboard-card-header">
                <h3>数据分布概览</h3>
                <div className="dashboard-card-filter">
                  <select>
                    <option>最近7天</option>
                    <option>最近30天</option>
                    <option>全部</option>
                  </select>
                </div>
              </div>
              <div className="dashboard-card-body">
                <div className="dashboard-chart-placeholder">
                  <div className="dashboard-chart-bar" style={{ height: '70%', backgroundColor: '#1890ff' }}></div>
                  <div className="dashboard-chart-bar" style={{ height: '85%', backgroundColor: '#52c41a' }}></div>
                  <div className="dashboard-chart-bar" style={{ height: '60%', backgroundColor: '#faad14' }}></div>
                  <div className="dashboard-chart-bar" style={{ height: '90%', backgroundColor: '#f5222d' }}></div>
                  <div className="dashboard-chart-bar" style={{ height: '75%', backgroundColor: '#13c2c2' }}></div>
                  <div className="dashboard-chart-bar" style={{ height: '65%', backgroundColor: '#722ed1' }}></div>
                  <div className="dashboard-chart-bar" style={{ height: '80%', backgroundColor: '#fa8c16' }}></div>
                </div>
              </div>
            </div>

            {/* 通知中心卡片 */}
            <div className="dashboard-card">
              <div className="dashboard-card-header">
                <h3>通知中心</h3>
                <span className="dashboard-notification-badge">{notifications.filter(n => !n.isRead).length}</span>
              </div>
              <div className="dashboard-card-body">
                <div className="dashboard-notifications">
                  {notifications.map(notification => (
                    <div key={notification.id} className={`dashboard-notification ${!notification.isRead ? 'unread' : ''}`}>
                      <div className="dashboard-notification-content">
                        <p>{notification.message}</p>
                        <span className="dashboard-notification-time">{notification.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;