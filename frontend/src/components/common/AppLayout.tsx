import { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Space, Typography } from 'antd';
import {
  UserOutlined,
  RobotOutlined,
  AppstoreOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  DashboardOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { ROUTES } from '@/utils/constants';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

export const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const menuItems: MenuProps['items'] = [
    {
      key: ROUTES.DASHBOARD,
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: ROUTES.DIGITAL_HUMANS,
      icon: <RobotOutlined />,
      label: 'Digital Humans',
    },
    {
      key: ROUTES.PLUGINS,
      icon: <AppstoreOutlined />,
      label: 'Plugins',
    },
    {
      key: ROUTES.AGENTS,
      icon: <TeamOutlined />,
      label: 'Agents',
    },
    {
      key: ROUTES.SCHEDULER,
      icon: <ClockCircleOutlined />,
      label: 'Scheduler',
    },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: () => {
        logout();
        navigate(ROUTES.LOGIN);
      },
    },
  ];

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    navigate(e.key);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: 20,
            fontWeight: 'bold',
          }}
        >
          {collapsed ? 'OU' : 'OpenUser'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            {collapsed ? (
              <MenuUnfoldOutlined
                style={{ fontSize: 18, cursor: 'pointer' }}
                onClick={() => setCollapsed(false)}
              />
            ) : (
              <MenuFoldOutlined
                style={{ fontSize: 18, cursor: 'pointer' }}
                onClick={() => setCollapsed(true)}
              />
            )}
          </div>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <Text>{user?.username}</Text>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff', minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};
