import { Card, Row, Col, Statistic, Typography } from 'antd';
import { RobotOutlined, AppstoreOutlined, TeamOutlined, ClockCircleOutlined } from '@ant-design/icons';

const { Title } = Typography;

export const DashboardPage: React.FC = () => {
  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Digital Humans"
              value={0}
              prefix={<RobotOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Plugins"
              value={0}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Agents"
              value={0}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Scheduled Tasks"
              value={0}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
