import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
} from '@mui/material';
import FactoryIcon from '@mui/icons-material/Factory';

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();

  const getTabValue = () => {
    if (location.pathname.startsWith('/assets')) return 1;
    if (location.pathname === '/upload') return 2;
    return 0;
  };

  const handleTabChange = (event, newValue) => {
    const routes = ['/', '/assets', '/upload'];
    navigate(routes[newValue]);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <FactoryIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            PowerPlant-PMS
          </Typography>
        </Toolbar>
        <Tabs
          value={getTabValue()}
          onChange={handleTabChange}
          textColor="inherit"
          indicatorColor="secondary"
        >
          <Tab label="대시보드" />
          <Tab label="자산 관리" />
          <Tab label="업로드" />
        </Tabs>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {children}
      </Container>
    </Box>
  );
}

export default Layout;

