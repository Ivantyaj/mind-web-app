import React from 'react';
import { Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { Home, SelfImprovement, Psychology, Person } from '@mui/icons-material';
import './Navigation.css';

const Navigation: React.FC = () => {
  return (
    <AppBar position="fixed" sx={{ top: 'auto', bottom: 0 }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ display: { xs: 'none', sm: 'block' } }}>
          MindfulnessApp
        </Typography>
        <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'space-around' }}>
          <Link to="/" className="nav-link">
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Home />
              <Typography variant="caption">Главная</Typography>
            </Box>
          </Link>
          <Link to="/meditation" className="nav-link">
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <SelfImprovement />
              <Typography variant="caption">Медитация</Typography>
            </Box>
          </Link>
          <Link to="/tests" className="nav-link">
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Psychology />
              <Typography variant="caption">Тесты</Typography>
            </Box>
          </Link>
          <Link to="/profile" className="nav-link">
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Person />
              <Typography variant="caption">Профиль</Typography>
            </Box>
          </Link>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation; 