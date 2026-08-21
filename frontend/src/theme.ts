/**
 * src/theme.ts
 * antd 5 暗色主题 —— 映射 Sentri 设计系统 tokens
 */
import { theme } from 'antd';
import type { ThemeConfig } from 'antd';

export const sentriTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    // 品牌色
    colorPrimary: '#6a5fc1',          // accent-violet：主交互
    colorInfo: '#6a5fc1',
    colorSuccess: '#c2ef4e',          // accent-lime（仅成功语义）
    colorWarning: '#fa7faa',          // accent-pink
    colorError: '#e5484d',
    colorLink: '#6a5fc1',

    // 画布与表面
    colorBgBase: '#1f1633',           // surface-canvas-dark
    colorBgContainer: '#150f23',      // surface-night（卡片）
    colorBgElevated: '#241a3d',       // 浮层
    colorBgLayout: '#1f1633',

    // 边框
    colorBorder: '#362d59',           // hairline-violet
    colorBorderSecondary: '#2c2347',

    // 文字
    colorText: '#ffffff',
    colorTextSecondary: 'rgba(255,255,255,0.72)',
    colorTextTertiary: 'rgba(255,255,255,0.52)',
    colorTextQuaternary: 'rgba(255,255,255,0.32)',

    // 字体与圆角
    fontFamily:
      "'Rubik', -apple-system, system-ui, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif",
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,

    // 控件尺寸
    controlHeight: 38,
    fontSize: 14,
  },
  components: {
    Button: {
      fontWeight: 700,
      primaryShadow: 'none',
      defaultBorderColor: '#362d59',
    },
    Card: {
      colorBgContainer: '#150f23',
      borderRadiusLG: 12,
    },
    Table: {
      colorBgContainer: '#150f23',
      headerBg: '#1f1633',
      borderColor: '#2c2347',
      rowHoverBg: '#241a3d',
    },
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: 'rgba(106,95,193,0.22)',
      itemSelectedColor: '#ffffff',
      itemHoverBg: 'rgba(255,255,255,0.06)',
      itemBorderRadius: 8,
    },
    Steps: {
      colorPrimary: '#c2ef4e',
    },
    Upload: {
      colorBgContainer: '#150f23',
    },
    Tag: {
      defaultBg: '#150f23',
      defaultColor: '#ffffff',
    },
  },
};
