import React from 'react';
import { Typography, Container, Box } from '@mui/material';

const Tests: React.FC = () => {
  return (
    <Container maxWidth="sm">
      <Box sx={{ pt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Психологические тесты
        </Typography>
        <Typography variant="body1" paragraph>
          Здесь будут доступны различные психологические тесты для самопознания.
        </Typography>
      </Box>
    </Container>
  );
};

export default Tests; 