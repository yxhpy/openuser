import { Card, Row, Col, Statistic, Typography } from 'antd';
import { RobotOutlined, AppstoreOutlined, TeamOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { listDigitalHumans } from '../../api/digitalHuman';
import { pluginApi } from '../../api/plugins';
import { listAgents } from '../../api/agents';
import { listTasks } from '../../api/scheduler';

const { Title } = Typography;

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState({
    digitalHumans: 0,
    plugins: 0,
    agents: 0,
    tasks: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [digitalHumansRes, pluginsRes, agentsRes, tasksRes] = await Promise.all([
          listDigitalHumans().catch(() => ({ digital_humans: [] })),
          pluginApi.list().catch(() => ({ plugins: [], total: 0 })),
          listAgents().catch(() => ({ agents: [], total: 0 })),
          listTasks().catch(() => ({ tasks: [], total: 0 })),
        ]);

        setStats({
          digitalHumans: digitalHumansRes.digital_humans?.length || 0,
          plugins: pluginsRes.total || 0,
          agents: agentsRes.total || 0,
          tasks: tasksRes.total || 0,
        });
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="Digital Humans"
              value={stats.digitalHumans}
              prefix={<RobotOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="Plugins"
              value={stats.plugins}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="Agents"
              value={stats.agents}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="Scheduled Tasks"
              value={stats.tasks}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
