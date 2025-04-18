import React from 'react';
import { Box, IconButton, Dialog, DialogContent } from '@mui/material';
import { Close } from '@mui/icons-material';

interface YouTubePlayerProps {
  videoId: string;
  open: boolean;
  onClose: () => void;
}

const YouTubePlayer: React.FC<YouTubePlayerProps> = ({ videoId, open, onClose }) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: 'black',
          position: 'relative',
        },
      }}
    >
      <IconButton
        onClick={onClose}
        sx={{
          position: 'absolute',
          right: 8,
          top: 8,
          color: 'white',
          zIndex: 1,
        }}
      >
        <Close />
      </IconButton>
      <DialogContent sx={{ p: 0, aspectRatio: '16/9' }}>
        <Box sx={{ width: '100%', height: '100%' }}>
          <iframe
            width="100%"
            height="100%"
            src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`}
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default YouTubePlayer; 