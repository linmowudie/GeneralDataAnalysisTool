import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

interface DashboardProps {
  onTabChange: (tab: 'dashboard' | 'analysis' | 'visualization') => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onTabChange }) => {
  const navigate = useNavigate();

  const handleTabChange = (tab: 'dashboard' | 'analysis' | 'visualization') => {
    switch (tab) {
      case 'analysis':
        navigate('/analysis');
        break;
      case 'visualization':
        navigate('/visualization');
        break;
      default:
        navigate('/');
    }
  };
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

  // 用户信息
  const userInfo = {
    name: '数据分析用户',
    role: '高级分析师',
    department: '数据科学部',
    lastLogin: '2024-05-20 09:30',
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>通用数据分析工具</h2>
        <div className="dashboard-tabs">
          <button className="tab-button active" onClick={() => handleTabChange('dashboard')}>仪表盘</button>
          <button className="tab-button" onClick={() => handleTabChange('analysis')}>数据分析</button>
          <button className="tab-button" onClick={() => handleTabChange('visualization')}>绘图</button>
        </div>
      </div>

      {/* 仪表盘内容区域 - 按照设计图布局 */}
      <div className="dashboard-dashboard-content">
        {/* 主要内容区域 - 6+1布局 */}
        <div className="dashboard-grid-layout">
          {/* 左侧6个卡片区域 */}
          <div className="dashboard-left-6cards">
            {/* 第一行 */}
            <div className="dashboard-grid-row">
              {/* 快速操作卡片 */}
              <div className="dashboard-grid-card">
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

              {/* 总项目卡片 */}
              <div className="dashboard-grid-card">
                <div className="dashboard-card-header">
                  <h3>总项目</h3>
                </div>
                <div className="dashboard-card-body">
                  <div className="dashboard-stat-display">
                    <p className="dashboard-stat-value-large">{dataStats.totalProjects}</p>
                    <p className="dashboard-stat-detail">
                      已完成: <span className="stat-success">{dataStats.completedProjects}</span>
                    </p>
                    <p className="dashboard-stat-detail">
                      进行中: <span className="stat-warning">{dataStats.pendingProjects}</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 第二行 */}
            <div className="dashboard-grid-row">
              {/* 最近项目卡片 */}
              <div className="dashboard-grid-card">
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

              {/* 进行中项目卡片 */}
              <div className="dashboard-grid-card">
                <div className="dashboard-card-header">
                  <h3>进行中</h3>
                </div>
                <div className="dashboard-card-body">
                  <div className="dashboard-progress-projects">
                    {recentProjects.filter(p => p.status === '进行中').map(project => (
                      <div key={project.id} className="dashboard-progress-item">
                        <div className="dashboard-progress-info">
                          <span className="dashboard-progress-name">{project.name}</span>
                          <span className="dashboard-progress-date">{project.date}</span>
                        </div>
                        <div className="dashboard-progress-bar">
                          <div className="dashboard-progress-fill" style={{ width: `${Math.random() * 80 + 20}%` }}></div>
                        </div>
                      </div>
                    ))}
                    {recentProjects.filter(p => p.status === '进行中').length === 0 && (
                      <div className="dashboard-no-projects">暂无进行中项目</div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* 第三行 */}
            <div className="dashboard-grid-row">
              {/* 通知卡片 */}
              <div className="dashboard-grid-card">
                <div className="dashboard-card-header">
                  <h3>通知</h3>
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

              {/* 已处理数据卡片 */}
              <div className="dashboard-grid-card">
                <div className="dashboard-card-header">
                  <h3>已处理数据</h3>
                </div>
                <div className="dashboard-card-body">
                  <div className="dashboard-data-stats">
                    <p className="dashboard-stat-value-large">{dataStats.totalDataSize}</p>
                    <div className="dashboard-data-types">
                      <div className="dashboard-data-type-item">
                        <span className="dashboard-data-type-color csv"></span>
                        <span className="dashboard-data-type-name">CSV文件</span>
                        <span className="dashboard-data-type-size">1.2GB</span>
                      </div>
                      <div className="dashboard-data-type-item">
                        <span className="dashboard-data-type-color excel"></span>
                        <span className="dashboard-data-type-name">Excel文件</span>
                        <span className="dashboard-data-type-size">800MB</span>
                      </div>
                      <div className="dashboard-data-type-item">
                        <span className="dashboard-data-type-color db"></span>
                        <span className="dashboard-data-type-name">数据库</span>
                        <span className="dashboard-data-type-size">500MB</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 右侧用户信息区域 */}
          <div className="dashboard-right-userarea">
            <div className="dashboard-user-info-card">
              <div className="dashboard-user-avatar">
                <div className="avatar-placeholder">头像</div>
              </div>
              <div className="dashboard-user-details">
                <h4>{userInfo.name}</h4>
                <p className="dashboard-user-role">{userInfo.role}</p>
                <p className="dashboard-user-department">{userInfo.department}</p>
                <p className="dashboard-user-lastlogin">上次登录: {userInfo.lastLogin}</p>
              </div>
              <div className="dashboard-user-actions">
                <button className="dashboard-user-action-btn">设置</button>
                <button className="dashboard-user-action-btn logout">退出登录</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;