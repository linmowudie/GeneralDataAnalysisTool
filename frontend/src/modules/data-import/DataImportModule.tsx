import React, { useState } from 'react';
import { Upload, Button, Form, Input, InputNumber, Select, Tabs, message } from 'antd';
import { InboxOutlined, DatabaseOutlined, FileOutlined, EyeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/common/Common';
import { useSession } from '../../context/SessionContext';
import { dataImportService } from '../../services/dataImportService';
import './DataImportModule.css';

const { Dragger } = Upload;

const DataImportModule: React.FC = () => {
  const navigate = useNavigate();
  const { refreshStatus } = useSession();
  const [uploading, setUploading] = useState(false);
  const [dbLoading, setDbLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [form] = Form.useForm();

  const handleUpload = async (file: File) => {
    setUploading(true);
    setResult(null);
    try {
      const res = await dataImportService.uploadFile(file);
      setResult(res);
      message.success(`文件 ${file.name} 导入成功`);
      await refreshStatus();
    } catch (e: any) {
      message.error(`导入失败：${e?.message || e}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDbImport = async (values: any) => {
    setDbLoading(true);
    setResult(null);
    try {
      const res = await dataImportService.importFromDatabase(
        values.db_type, values.host, values.port, values.database, values.table,
        values.username, values.password
      );
      setResult(res);
      message.success('数据库导入成功');
      await refreshStatus();
    } catch (e: any) {
      message.error(`导入失败：${e?.message || e}`);
    } finally {
      setDbLoading(false);
    }
  };

  return (
    <div className="df-page">
      <PageHeader
        eyebrow="STEP 01 · IMPORT"
        title={
          <>
            数据<span className="df-lime-chip">导入</span>
          </>
        }
        description="支持 CSV / Excel / JSON / HTML / SQLite 文件上传，以及 MySQL、PostgreSQL、SQLite、MongoDB 数据库导入。"
        extra={
          result && (
            <Button type="primary" icon={<EyeOutlined />} onClick={() => navigate('/preview')}>
              前往预览
            </Button>
          )
        }
      />

      <div className="df-card df-card-lg">
        <Tabs
          defaultActiveKey="file"
          items={[
            {
              key: 'file',
              label: (<span><FileOutlined /> 文件上传</span>),
              children: (
                <Dragger
                  accept=".csv,.xls,.xlsx,.json,.html,.db,.sqlite"
                  multiple={false}
                  showUploadList={false}
                  customRequest={({ file }) => handleUpload(file as File)}
                  disabled={uploading}
                >
                  <p className="ant-upload-drag-icon"><InboxOutlined /></p>
                  <p className="ant-upload-text df-upload-title">点击或拖拽文件到此处上传</p>
                  <p className="ant-upload-hint df-caption">
                    {uploading ? '正在导入，请稍候…' : '单次上传一个数据文件，导入后即可进入预览与清洗'}
                  </p>
                </Dragger>
              ),
            },
            {
              key: 'db',
              label: (<span><DatabaseOutlined /> 数据库导入</span>),
              children: (
                <Form form={form} layout="vertical" onFinish={handleDbImport} className="df-db-form"
                  initialValues={{ db_type: 'mysql', host: 'localhost', port: 3306 }}>
                  <div className="df-grid-2">
                    <Form.Item name="db_type" label="数据库类型" rules={[{ required: true }]}>
                      <Select options={[
                        { value: 'mysql', label: 'MySQL' },
                        { value: 'postgresql', label: 'PostgreSQL' },
                        { value: 'sqlite', label: 'SQLite' },
                        { value: 'mongodb', label: 'MongoDB' },
                      ]} />
                    </Form.Item>
                    <Form.Item name="host" label="主机" rules={[{ required: true }]}>
                      <Input placeholder="localhost" />
                    </Form.Item>
                    <Form.Item name="port" label="端口" rules={[{ required: true }]}>
                      <InputNumber style={{ width: '100%' }} min={1} max={65535} />
                    </Form.Item>
                    <Form.Item name="database" label="数据库名" rules={[{ required: true }]}>
                      <Input placeholder="database name" />
                    </Form.Item>
                    <Form.Item name="table" label="表名 / 集合" rules={[{ required: true }]}>
                      <Input placeholder="table name" />
                    </Form.Item>
                    <Form.Item name="username" label="用户名">
                      <Input placeholder="可选" />
                    </Form.Item>
                    <Form.Item name="password" label="密码">
                      <Input.Password placeholder="可选" />
                    </Form.Item>
                  </div>
                  <Button type="primary" htmlType="submit" loading={dbLoading}>开始导入</Button>
                </Form>
              ),
            },
          ]}
        />
      </div>

      {result && (
        <div className="df-card df-import-result">
          <div className="df-eyebrow">IMPORT RESULT</div>
          <div className="df-card-title">{result.file_name || result.message || '导入完成'}</div>
          <pre className="df-code df-result-json">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default DataImportModule;
