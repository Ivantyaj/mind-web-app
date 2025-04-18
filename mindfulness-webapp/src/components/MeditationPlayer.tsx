import React from 'react';
import { Box, Typography, IconButton, Paper } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import useTelegram from '../hooks/useTelegram';
import PremiumContent from './PremiumContent';

interface MeditationPlayerProps {
  videoId: string;
  title: string;
  description: string;
  image: string;
  isPremium: boolean;
  onBack: () => void;
}

const MeditationPlayer: React.FC<MeditationPlayerProps> = ({
  videoId,
  title,
  description,
  image,
  isPremium,
  onBack,
}) => {
  const { user } = useTelegram();

  return (
    <Box>
      {/* Заголовок с кнопкой назад */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={onBack} sx={{ mr: 1 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h5" component="h2">
          {title}
        </Typography>
      </Box>

      {/* Контент (видео или премиум-блок) */}
      {isPremium && !user?.is_premium ? (
        <PremiumContent
          title={title}
          description={description}
          image={image}
        />
      ) : (
        <>
          <Paper 
            elevation={3}
            sx={{
              position: 'relative',
              width: '100%',
              paddingTop: '56.25%', // Соотношение сторон 16:9
              mb: 2,
            }}
          >
            <iframe
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                border: 0,
              }}
              src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`}
              title="YouTube video player"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </Paper>

          {/* Описание */}
          <Typography variant="body1" color="text.secondary">
            {description}
          </Typography>
        </>
      )}
    </Box>
  );
};

export default MeditationPlayer; 