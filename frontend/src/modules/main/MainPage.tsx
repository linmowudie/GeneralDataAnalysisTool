import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Dashboard from '../dashboard/Dashboard';
import DataAnalysis from '../analysis/DataAnalysis';
import './MainPage.css';

const MainPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analysis' | 'visualization'>('dashboard');
  const navigate = useNavigate();
  const location = useLocation();

  // 根据URL设置初始标签页
  useEffect(() => {
    const path = location.pathname;
    if (path === '/analysis') {
      setActiveTab('analysis');
    } else if (path === '/visualization') {
      setActiveTab('visualization');
    } else {
      setActiveTab('dashboard');
    }
  }, [location]);

  const handleTabChange = (tab: 'dashboard' | 'analysis' | 'visualization') => {
    setActiveTab(tab);
    // 更新URL但不刷新页面
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

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onTabChange={handleTabChange} />;
      case 'analysis':
        return <DataAnalysis onTabChange={handleTabChange} />;
      case 'visualization':
        // 绘图界面将在后续实现
        return <div className="placeholder">绘图功能即将上线</div>;
      default:
        return <Dashboard onTabChange={handleTabChange} />;
    }
  };

  return (
    <div className="main-page-container">
      {renderContent()}
    </div>
  );
};

export default MainPage;