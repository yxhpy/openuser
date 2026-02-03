import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  message,
  Tag,
  Tooltip,
  Spin,
  Empty,
} from 'antd';
import {
  ReloadOutlined,
  PlusOutlined,
  ApiOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { pluginApi, PluginInfo } from '../../api/plugins';

const { Title, Text, Paragraph } = Typography;

export const PluginsPage: React.FC = () => {
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [installModalVisible, setInstallModalVisible] = useState(false);
  const [reloadingPlugin, setReloadingPlugin] = useState<string | null>(null);
  const [form] = Form.useForm();

  // Load plugins on mount
  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = async () => {
    setLoading(true);
    try {
      const response = await pluginApi.list();
      setPlugins(response.plugins);
      message.success(`Loaded ${response.total} plugin(s)`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to load plugins');
    } finally {
      setLoading(false);
    }
  };

  const handleInstall = async (values: { name: string }) => {
    try {
      const response = await pluginApi.install({ name: values.name });
      message.success(response.message);
      setInstallModalVisible(false);
      form.resetFields();
      await loadPlugins();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to install plugin');
    }
  };

  const handleReload = async (pluginName: string) => {
    setReloadingPlugin(pluginName);
    try {
      const response = await pluginApi.reload({ name: pluginName });
      message.success(response.message);
      await loadPlugins();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to reload plugin');
    } finally {
      setReloadingPlugin(null);
    }
  };

  const columns = [
    {
      title: 'Plugin Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Space>
          <ApiOutlined style={{ color: '#1890ff' }} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
      render: (version: string) => <Tag color="blue">{version}</Tag>,
    },
    {
      title: 'Dependencies',
      dataIndex: 'dependencies',
      key: 'dependencies',
      render: (dependencies: string[]) => (
        <Space wrap>
          {dependencies.length > 0 ? (
            dependencies.map((dep) => (
              <Tag key={dep} color="geekblue">
                {dep}
              </Tag>
            ))
          ) : (
            <Text type="secondary">No dependencies</Text>
          )}
        </Space>
      ),
    },
    {
      title: 'Status',
      key: 'status',
      render: () => (
        <Tag icon={<CheckCircleOutlined />} color="success">
          Active
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: PluginInfo) => (
        <Space>
          <Tooltip title="Hot-reload plugin without restart">
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              loading={reloadingPlugin === record.name}
              onClick={() => handleReload(record.name)}
              size="small"
            >
              Reload
            </Button>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Title level={2} style={{ margin: 0 }}>
                Plugin Management
              </Title>
              <Paragraph type="secondary" style={{ margin: '8px 0 0 0' }}>
                Manage and hot-reload plugins without system restart
              </Paragraph>
            </div>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadPlugins}
                loading={loading}
              >
                Refresh
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setInstallModalVisible(true)}
              >
                Install Plugin
              </Button>
            </Space>
          </div>

          {/* Statistics */}
          <Card size="small" style={{ background: '#f0f2f5' }}>
            <Space size="large">
              <div>
                <Text type="secondary">Total Plugins</Text>
                <Title level={4} style={{ margin: '4px 0 0 0' }}>
                  {plugins.length}
                </Title>
              </div>
              <div>
                <Text type="secondary">Active Plugins</Text>
                <Title level={4} style={{ margin: '4px 0 0 0', color: '#52c41a' }}>
                  {plugins.length}
                </Title>
              </div>
            </Space>
          </Card>

          {/* Plugin Table */}
          <Spin spinning={loading}>
            {plugins.length > 0 ? (
              <Table
                columns={columns}
                dataSource={plugins}
                rowKey="name"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showTotal: (total) => `Total ${total} plugins`,
                }}
              />
            ) : (
              <Empty
                description="No plugins installed"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setInstallModalVisible(true)}
                >
                  Install Your First Plugin
                </Button>
              </Empty>
            )}
          </Spin>
        </Space>
      </Card>

      {/* Install Plugin Modal */}
      <Modal
        title="Install Plugin"
        open={installModalVisible}
        onCancel={() => {
          setInstallModalVisible(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleInstall}
        >
          <Form.Item
            label="Plugin Name"
            name="name"
            rules={[
              { required: true, message: 'Please enter plugin name' },
              { min: 1, max: 100, message: 'Plugin name must be 1-100 characters' },
            ]}
          >
            <Input
              placeholder="e.g., image-processor, video-editor"
              prefix={<ApiOutlined />}
            />
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => {
                setInstallModalVisible(false);
                form.resetFields();
              }}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                Install
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
