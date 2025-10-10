// 数据分析相关类型定义

export interface DataPreview {
  success: boolean;
  file_name: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  preview_data: Record<string, any>[];
  [key: string]: any;
}

export interface DatasetInfo {
  dataset_name: string;
  total_records: number;
  features_count: number;
  target_variable: string;
  data_types: Record<string, string>;
  [key: string]: any;
}

export interface AnalysisParameters {
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
}

export interface CleaningParameters {
  custom_params?: string[];
}

export interface VisualizationParameters {
  task_type?: string;
  model_name?: string;
  feature?: any;
  target?: any;
  predict?: any;
}

export interface DatabaseImportParameters {
  db_type: string;
  host: string;
  port: number;
  database: string;
  table: string;
  username?: string;
  password?: string;
}