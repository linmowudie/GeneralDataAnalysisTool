// API服务封装
const API_BASE_URL = 'http://localhost:8000/api';

interface ApiResponse<T> {
  success?: boolean;
  message?: string;
  data?: T;
  [key: string]: any;
}

// 创建会话
export async function createSession(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/import/create-session`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('创建会话失败');
  }
  
  const data = await response.json();
  return data.session_id;
}

// 上传文件
export async function uploadFile(sessionId: string, file: File): Promise<ApiResponse<any>> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/import/upload-file`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('文件上传失败');
  }
  
  return await response.json();
}

// 从数据库导入
export async function importFromDatabase(
  sessionId: string,
  dbType: string,
  host: string,
  port: number,
  database: string,
  table: string,
  username?: string,
  password?: string
): Promise<ApiResponse<any>> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('db_type', dbType);
  formData.append('host', host);
  formData.append('port', port.toString());
  formData.append('database', database);
  formData.append('table', table);
  if (username) formData.append('username', username);
  if (password) formData.append('password', password);
  
  const response = await fetch(`${API_BASE_URL}/import/import-from-database`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('数据库导入失败');
  }
  
  return await response.json();
}

// 结束会话
export async function endSession(sessionId: string): Promise<ApiResponse<any>> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  
  const response = await fetch(`${API_BASE_URL}/import/end-session`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('结束会话失败');
  }
  
  return await response.json();
}

// 获取数据预览
export async function getDataPreview(sessionId: string): Promise<ApiResponse<any>> {
  const response = await fetch(`${API_BASE_URL}/preview/data-preview?session_id=${sessionId}`);
  
  if (!response.ok) {
    throw new Error('获取数据预览失败');
  }
  
  return await response.json();
}

// 获取数据集信息
export async function getDatasetInfo(sessionId: string): Promise<ApiResponse<any>> {
  const response = await fetch(`${API_BASE_URL}/preview/dataset-info?session_id=${sessionId}`);
  
  if (!response.ok) {
    throw new Error('获取数据集信息失败');
  }
  
  return await response.json();
}

// 数据清洗
export async function cleanData(
  sessionId: string,
  mode: string,
  isCustom: boolean = false,
  parameters: {
    custom_params?: string[];
  } = {},
  targetCol?: string
): Promise<ApiResponse<any>> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('mode', mode);
  formData.append('is_custom', isCustom.toString());
  formData.append('parameters', JSON.stringify(parameters));
  if (targetCol) {
    formData.append('target_col', targetCol);
  }
  
  const response = await fetch(`${API_BASE_URL}/cleaning/clean-data`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('数据清洗失败');
  }
  
  return await response.json();
}

// 获取清洗模式
export async function getCleaningModes(): Promise<ApiResponse<string[]>> {
  const response = await fetch(`${API_BASE_URL}/cleaning/cleaning-modes`);
  
  if (!response.ok) {
    throw new Error('获取清洗模式失败');
  }
  
  return await response.json();
}

// 运行分析
export async function runAnalysis(
  sessionId: string,
  modelType: string,
  parameters: {
    random_state?: number;
    is_split?: boolean;
    split_ratio?: number;
    feature_cols?: string[];
    target_col?: string;
    is_return_model_param?: boolean;
    metrics_list?: string[];
    is_return_model_score?: boolean;
    is_return_training_set?: boolean;
    is_return_model_predicting_set?: boolean;
    feature_cols_encoding?: string;
    target_col_encoding?: string;
    test_set?: any;
    model_params?: Record<string, any>;
  } = {}
): Promise<ApiResponse<any>> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('model_type', modelType);
  formData.append('parameters', JSON.stringify(parameters));
  
  const response = await fetch(`${API_BASE_URL}/analysis/run-analysis`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('数据分析失败');
  }
  
  return await response.json();
}

// 获取可用模型
export async function getAvailableModels(): Promise<ApiResponse<string[]>> {
  const response = await fetch(`${API_BASE_URL}/analysis/available-models`);
  
  if (!response.ok) {
    throw new Error('获取可用模型失败');
  }
  
  return await response.json();
}

// 生成图表
export async function generateChart(
  sessionId: string,
  chartType: string,
  parameters: {
    task_type?: string;
    model_name?: string;
    feature?: any;
    target?: any;
    predict?: any;
  } = {}
): Promise<ApiResponse<any>> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('chart_type', chartType);
  formData.append('parameters', JSON.stringify(parameters));
  
  const response = await fetch(`${API_BASE_URL}/visualization/generate-chart`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('生成图表失败');
  }
  
  return await response.json();
}

// 获取可用图表类型
export async function getAvailableCharts(): Promise<ApiResponse<string[]>> {
  const response = await fetch(`${API_BASE_URL}/visualization/available-charts`);
  
  if (!response.ok) {
    throw new Error('获取可用图表类型失败');
  }
  
  return await response.json();
}