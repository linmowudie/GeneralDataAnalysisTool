/// <reference types="vite/client" />

// 声明Vite环境变量的类型
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  // 可以添加其他环境变量类型
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}