import React from 'react';
import { Typography, Container, Box } from '@mui/material';

const Profile: React.FC = () => {
  return (
    <Container maxWidth="sm">
      <Box sx={{ pt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Профиль
        </Typography>
        <Typography variant="body1" paragraph>
          Здесь будет отображаться информация о вашем профиле и прогрессе.
        </Typography>
      </Box>
    </Container>
  );
};

export default Profile; 