import React from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
} from '@mui/material';
import { Lock, Star } from '@mui/icons-material';
import useTelegram from '../hooks/useTelegram';

interface PremiumContentProps {
  title: string;
  description: string;
  image: string;
}

const PremiumContent: React.FC<PremiumContentProps> = ({
  title,
  description,
  image,
}) => {
  const { openPremiumBot } = useTelegram();

  return (
    <Box>
      <Paper
        sx={{
          position: 'relative',
          width: '100%',
          paddingTop: '56.25%',
          mb: 2,
          overflow: 'hidden',
        }}
      >
        {/* Затемненное изображение */}
        <Box
          component="img"
          src={image}
          alt={title}
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'brightness(0.3)',
          }}
        />
        
        {/* Оверлей с информацией */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 3,
            textAlign: 'center',
            color: 'white',
          }}
        >
          <Lock sx={{ fontSize: 48, mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Премиум контент
          </Typography>
          <Typography variant="body1" sx={{ mb: 3 }}>
            Эта медитация доступна только для премиум-пользователей
          </Typography>
          <Button
            variant="contained"
            startIcon={<Star />}
            onClick={openPremiumBot}
            sx={{
              backgroundColor: 'gold',
              color: 'black',
              '&:hover': {
                backgroundColor: '#ffd700',
              },
            }}
          >
            Получить премиум доступ
          </Button>
        </Box>
      </Paper>

      <Typography variant="h5" gutterBottom>
        {title}
      </Typography>
      <Typography variant="body1" color="text.secondary">
        {description}
      </Typography>
    </Box>
  );
};

export default PremiumContent; 