import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  Table,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { listTasks, createTask, updateTask, deleteTask } from '../../api/scheduler';
import type { TaskResponse, TaskCreateRequest, TaskUpdateRequest } from '../../types/generated';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// Task types
const TASK_TYPES = [
  { value: 'video_generation', label: 'Video Generation' },
  { value: 'voice_synthesis', label: 'Voice Synthesis' },
  { value: 'face_animation', label: 'Face Animation' },
  { value: 'report_generation', label: 'Report Generation' },
  { value: 'batch_processing', label: 'Batch Processing' },
  { value: 'custom', label: 'Custom' },
];

// Task statuses
const TASK_STATUSES = [
  { value: 'pending', label: 'Pending', color: 'default' },
  { value: 'running', label: 'Running', color: 'processing' },
  { value: 'completed', label: 'Completed', color: 'success' },
  { value: 'failed', label: 'Failed', color: 'error' },
  { value: 'cancelled', label: 'Cancelled', color: 'warning' },
];

export const SchedulerPage: React.FC = () => {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskResponse | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | undefined>();
  const [filterType, setFilterType] = useState<string | undefined>();
  const [form] = Form.useForm();

  // Load tasks
  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await listTasks({
        status: filterStatus,
        task_type: filterType,
      });
      setTasks(response.tasks || []);
    } catch (error) {
      message.error('Failed to load tasks');
      console.error('Load tasks error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [filterStatus, filterType]);

  // Calculate statistics
  const stats = {
    total: tasks.length,
    pending: tasks.filter((t) => t.status === 'pending').length,
    running: tasks.filter((t) => t.status === 'running').length,
    completed: tasks.filter((t) => t.status === 'completed').length,
    failed: tasks.filter((t) => t.status === 'failed').length,
  };

  // Handle create/edit task
  const handleSubmit = async (values: any) => {
    try {
      if (editingTask) {
        // Update existing task
        const updateData: TaskUpdateRequest = {
          name: values.name,
          description: values.description,
          schedule: values.schedule,
          params: values.params ? JSON.parse(values.params) : null,
          status: values.status,
        };
        await updateTask(editingTask.id!, updateData);
        message.success('Task updated successfully');
      } else {
        // Create new task
        const createData: TaskCreateRequest = {
          name: values.name,
          description: values.description,
          task_type: values.task_type,
          schedule: values.schedule,
          params: values.params ? JSON.parse(values.params) : null,
        };
        await createTask(createData);
        message.success('Task created successfully');
      }
      setIsModalVisible(false);
      form.resetFields();
      setEditingTask(null);
      loadTasks();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to save task');
      console.error('Save task error:', error);
    }
  };

  // Handle delete task
  const handleDelete = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      message.success('Task deleted successfully');
      loadTasks();
    } catch (error) {
      message.error('Failed to delete task');
      console.error('Delete task error:', error);
    }
  };

  // Handle edit task
  const handleEdit = (task: TaskResponse) => {
    setEditingTask(task);
    form.setFieldsValue({
      name: task.name,
      description: task.description,
      task_type: task.task_type,
      schedule: task.schedule,
      params: task.params ? JSON.stringify(task.params, null, 2) : '',
      status: task.status,
    });
    setIsModalVisible(true);
  };

  // Handle create new task
  const handleCreate = () => {
    setEditingTask(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  // Get status color
  const getStatusColor = (status?: string) => {
    const statusObj = TASK_STATUSES.find((s) => s.value === status);
    return statusObj?.color || 'default';
  };

  // Table columns
  const columns: ColumnsType<TaskResponse> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: 'Type',
      dataIndex: 'task_type',
      key: 'task_type',
      width: 150,
      render: (type: string) => {
        const taskType = TASK_TYPES.find((t) => t.value === type);
        return taskType?.label || type;
      },
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status?.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Schedule',
      dataIndex: 'schedule',
      key: 'schedule',
      width: 150,
      render: (schedule: string | null) => schedule || '-',
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure to delete this task?"
            onConfirm={() => handleDelete(record.id!)}
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
      <Title level={2}>Task Scheduler</Title>

      {/* Statistics Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <Card>
            <Statistic title="Total Tasks" value={stats.total} />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Pending"
              value={stats.pending}
              valueStyle={{ color: '#8c8c8c' }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Running"
              value={stats.running}
              valueStyle={{ color: '#1890ff' }}
              prefix={<PlayCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Completed"
              value={stats.completed}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Failed"
              value={stats.failed}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filters and Actions */}
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            Create Task
          </Button>
          <Button icon={<ReloadOutlined />} onClick={loadTasks}>
            Refresh
          </Button>
          <Select
            placeholder="Filter by Status"
            style={{ width: 150 }}
            allowClear
            onChange={setFilterStatus}
            value={filterStatus}
          >
            {TASK_STATUSES.map((status) => (
              <Option key={status.value} value={status.value}>
                {status.label}
              </Option>
            ))}
          </Select>
          <Select
            placeholder="Filter by Type"
            style={{ width: 180 }}
            allowClear
            onChange={setFilterType}
            value={filterType}
          >
            {TASK_TYPES.map((type) => (
              <Option key={type.value} value={type.value}>
                {type.label}
              </Option>
            ))}
          </Select>
        </Space>

        {/* Tasks Table */}
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} tasks`,
          }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingTask ? 'Edit Task' : 'Create Task'}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
          setEditingTask(null);
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
            label="Task Name"
            rules={[{ required: true, message: 'Please enter task name' }]}
          >
            <Input placeholder="Enter task name" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
          >
            <TextArea
              rows={3}
              placeholder="Enter task description"
            />
          </Form.Item>

          <Form.Item
            name="task_type"
            label="Task Type"
            rules={[{ required: !editingTask, message: 'Please select task type' }]}
          >
            <Select
              placeholder="Select task type"
              disabled={!!editingTask}
            >
              {TASK_TYPES.map((type) => (
                <Option key={type.value} value={type.value}>
                  {type.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="schedule"
            label="Schedule (Cron Expression)"
            help="e.g., '0 0 * * *' for daily at midnight"
          >
            <Input placeholder="Enter cron expression" />
          </Form.Item>

          <Form.Item
            name="params"
            label="Parameters (JSON)"
            help="Enter task parameters as JSON object"
          >
            <TextArea
              rows={4}
              placeholder='{"key": "value"}'
            />
          </Form.Item>

          {editingTask && (
            <Form.Item
              name="status"
              label="Status"
            >
              <Select placeholder="Select status">
                {TASK_STATUSES.map((status) => (
                  <Option key={status.value} value={status.value}>
                    {status.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          )}

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingTask ? 'Update' : 'Create'}
              </Button>
              <Button
                onClick={() => {
                  setIsModalVisible(false);
                  form.resetFields();
                  setEditingTask(null);
                }}
              >
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
