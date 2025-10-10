# 通用数据分析工具前端

这是一个基于 React + TypeScript + Vite 构建的数据分析工具前端界面。

## 项目结构

```
src/
├── App.css                 # 主样式文件
├── App.tsx                 # 主应用组件
├── main.tsx                # 应用入口文件
├── index.css               # 全局样式
├── assets/                 # 静态资源文件
├── services/               # API服务封装
│   └── api.ts             # API调用封装
└── hooks/                  # 自定义React Hooks
    ├── useSession.ts      # 会话管理Hook
    ├── useDataPreview.ts  # 数据预览Hook
    └── useApi.ts          # 通用API调用Hook
```

## 功能模块

1. **仪表板** - 显示数据概览和系统状态
2. **数据导入** - 支持文件、数据库和API三种方式导入数据
3. **数据预览** - 展示数据的基本信息和前几行数据
4. **数据清洗** - 提供多种数据清洗模式
5. **数据分析** - 支持多种机器学习模型进行数据分析
6. **数据可视化** - 生成各种类型的图表
7. **报表生成** - 生成分析报告

## 技术栈

- React 18
- TypeScript
- Vite
- CSS Modules

## 开发环境搭建

1. 确保已安装 Node.js (推荐版本 16+)
2. 在项目根目录下安装依赖：
   ```bash
   npm install
   ```
3. 启动开发服务器：
   ```bash
   npm run dev
   ```

## 构建与部署

- 构建生产版本：
  ```bash
  npm run build
  ```

- 预览生产构建：
  ```bash
  npm run preview
  ```

## API集成

前端通过调用后端API实现各种功能。API服务封装在 `src/services/api.ts` 文件中。

确保后端服务运行在 `http://localhost:8000`，或者在 `src/services/api.ts` 中修改 `API_BASE_URL` 常量。

## React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```