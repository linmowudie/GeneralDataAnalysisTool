import React, { useState } from 'react';
import Dashboard from '../dashboard/Dashboard';
import DataAnalysis from '../analysis/DataAnalysis';
import './MainPage.css';

const MainPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analysis' | 'visualization'>('dashboard');

  const handleTabChange = (tab: 'dashboard' | 'analysis' | 'visualization') => {
    setActiveTab(tab);
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