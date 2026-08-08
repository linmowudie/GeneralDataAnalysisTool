import { describe, it, expect } from 'vitest';
import { ApiError, ApiService, apiService } from '../apiService';

describe('ApiError', () => {
  it('保留 message、code 与 detail 字段', () => {
    const error = new ApiError('请求失败', 404, { reason: 'not found' });
    expect(error.name).toBe('ApiError');
    expect(error.message).toBe('请求失败');
    expect(error.code).toBe(404);
    expect(error.detail).toEqual({ reason: 'not found' });
    expect(error).toBeInstanceOf(Error);
  });
});

describe('ApiService 会话管理', () => {
  it('默认无会话，设置后可读取会话 ID', () => {
    const service = new ApiService('http://127.0.0.1:8000');
    expect(service.getSessionId()).toBeNull();
    service.setSessionId('session-123');
    expect(service.getSessionId()).toBe('session-123');
  });
});

describe('services 导出', () => {
  it('提供全局 apiService 单例', () => {
    expect(apiService).toBeInstanceOf(ApiService);
  });
});
