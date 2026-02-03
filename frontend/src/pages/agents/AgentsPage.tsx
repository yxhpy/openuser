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
  Popconfirm,
  Spin,
  Empty,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { listAgents, createAgent, updateAgent, deleteAgent } from '../../api/agents';
import type { AgentResponse, AgentCreateRequest, AgentUpdateRequest } from '../../types/generated';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

export const AgentsPage: React.FC = () => {
  const [agents, setAgents] = useState<AgentResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingAgent, setEditingAgent] = useState<AgentResponse | null>(null);
  const [form] = Form.useForm();

  // Load agents on mount
  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    setLoading(true);
    try {
      const response = await listAgents();
      setAgents(response.agents || []);
      message.success(`Loaded ${response.total || 0} agent(s)`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingAgent(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (agent: AgentResponse) => {
    setEditingAgent(agent);
    form.setFieldsValue({
      name: agent.name,
      system_prompt: agent.system_prompt,
      capabilities: agent.capabilities?.join(', '),
    });
    setIsModalVisible(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      const capabilities = values.capabilities
        ? values.capabilities.split(',').map((c: string) => c.trim()).filter((c: string) => c)
        : [];

      if (editingAgent) {
        // Update existing agent
        const updateData: AgentUpdateRequest = {
          system_prompt: values.system_prompt,
          capabilities,
        };
        await updateAgent(editingAgent.name!, updateData);
        message.success('Agent updated successfully');
      } else {
        // Create new agent
        const createData: AgentCreateRequest = {
          name: values.name,
          system_prompt: values.system_prompt,
          capabilities,
        };
        await createAgent(createData);
        message.success('Agent created successfully');
      }
      setIsModalVisible(false);
      form.resetFields();
      setEditingAgent(null);
      loadAgents();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to save agent');
    }
  };

  const handleDelete = async (name: string) => {
    try {
      await deleteAgent(name);
      message.success('Agent deleted successfully');
      loadAgents();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to delete agent');
    }
  };

  const columns: ColumnsType<AgentResponse> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Space>
          <RobotOutlined style={{ color: '#1890ff' }} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'System Prompt',
      dataIndex: 'system_prompt',
      key: 'system_prompt',
      ellipsis: true,
      render: (prompt: string) => (
        <Text ellipsis={{ tooltip: prompt }}>{prompt}</Text>
      ),
    },
    {
      title: 'Capabilities',
      dataIndex: 'capabilities',
      key: 'capabilities',
      render: (capabilities: string[]) => (
        <Space wrap>
          {capabilities && capabilities.length > 0 ? (
            capabilities.map((cap) => (
              <Tag key={cap} color="blue">
                {cap}
              </Tag>
            ))
          ) : (
            <Text type="secondary">No capabilities</Text>
          )}
        </Space>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_: any, record: AgentResponse) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure to delete this agent?"
            onConfirm={() => handleDelete(record.name!)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              Delete
            </Button>
          </Popconfirm>
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
                Agent Management
              </Title>
              <Paragraph type="secondary" style={{ margin: '8px 0 0 0' }}>
                Manage AI agents with custom prompts and capabilities
              </Paragraph>
            </div>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadAgents}
                loading={loading}
              >
                Refresh
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreate}
              >
                Create Agent
              </Button>
            </Space>
          </div>

          {/* Statistics */}
          <Card size="small" style={{ background: '#f0f2f5' }}>
            <Space size="large">
              <div>
                <Text type="secondary">Total Agents</Text>
                <Title level={4} style={{ margin: '4px 0 0 0' }}>
                  {agents.length}
                </Title>
              </div>
            </Space>
          </Card>

          {/* Agents Table */}
          <Spin spinning={loading}>
            {agents.length > 0 ? (
              <Table
                columns={columns}
                dataSource={agents}
                rowKey="name"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showTotal: (total) => `Total ${total} agents`,
                }}
              />
            ) : (
              <Empty
                description="No agents created"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleCreate}
                >
                  Create Your First Agent
                </Button>
              </Empty>
            )}
          </Spin>
        </Space>
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingAgent ? 'Edit Agent' : 'Create Agent'}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
          setEditingAgent(null);
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="Agent Name"
            rules={[
              { required: true, message: 'Please enter agent name' },
              { min: 1, max: 100, message: 'Name must be 1-100 characters' },
            ]}
          >
            <Input
              placeholder="e.g., assistant, researcher"
              disabled={!!editingAgent}
            />
          </Form.Item>

          <Form.Item
            name="system_prompt"
            label="System Prompt"
            rules={[{ required: true, message: 'Please enter system prompt' }]}
          >
            <TextArea
              rows={6}
              placeholder="You are a helpful AI assistant..."
            />
          </Form.Item>

          <Form.Item
            name="capabilities"
            label="Capabilities"
            help="Enter comma-separated capabilities (e.g., plugin-install, self-update)"
          >
            <Input placeholder="plugin-install, self-update, code-generation" />
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button
                onClick={() => {
                  setIsModalVisible(false);
                  form.resetFields();
                  setEditingAgent(null);
                }}
              >
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                {editingAgent ? 'Update' : 'Create'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
