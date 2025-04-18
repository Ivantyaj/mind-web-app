import React from 'react';
import { Typography, Container, Box } from '@mui/material';

const Home: React.FC = () => {
  return (
    <Container maxWidth="sm">
      <Box sx={{ pt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Добро пожаловать в MindfulnessApp
        </Typography>
        <Typography variant="body1" paragraph>
          Начните свой путь к осознанности и душевному равновесию вместе с нами.
        </Typography>
      </Box>
    </Container>
  );
};

export default Home; 