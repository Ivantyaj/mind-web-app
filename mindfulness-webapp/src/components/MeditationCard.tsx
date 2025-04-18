import React from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  CardActions,
  Button,
  Chip,
  Box,
} from '@mui/material';
import { AccessTime, PlayArrow } from '@mui/icons-material';

interface MeditationCardProps {
  title: string;
  description: string;
  duration: number; // в минутах
  image: string;
  category: string;
  isPremium?: boolean;
  onPlay: () => void;
}

const MeditationCard: React.FC<MeditationCardProps> = ({
  title,
  description,
  duration,
  image,
  category,
  isPremium = false,
  onPlay,
}) => {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardMedia
        component="img"
        height="140"
        image={image}
        alt={title}
        sx={{ objectFit: 'cover' }}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Typography gutterBottom variant="h6" component="h2" sx={{ mb: 0 }}>
            {title}
          </Typography>
          {isPremium && (
            <Chip
              label="Premium"
              color="primary"
              size="small"
              sx={{
                backgroundColor: 'gold',
                color: 'black',
                fontWeight: 'bold',
              }}
            />
          )}
        </Box>
        <Typography variant="body2" color="text.secondary" paragraph>
          {description}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            icon={<AccessTime fontSize="small" />}
            label={`${duration} мин`}
            size="small"
            variant="outlined"
          />
          <Chip
            label={category}
            size="small"
            variant="outlined"
            sx={{ ml: 1 }}
          />
        </Box>
      </CardContent>
      <CardActions>
        <Button
          fullWidth
          variant="contained"
          startIcon={<PlayArrow />}
          onClick={onPlay}
          sx={{
            mt: 'auto',
            backgroundColor: isPremium ? 'gold' : undefined,
            color: isPremium ? 'black' : undefined,
            '&:hover': {
              backgroundColor: isPremium ? '#ffd700' : undefined,
            },
          }}
        >
          Начать медитацию
        </Button>
      </CardActions>
    </Card>
  );
};

export default MeditationCard; 