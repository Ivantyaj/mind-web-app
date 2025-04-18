import React, { useState } from 'react';
import {
  Typography,
  Container,
  Box,
  Grid,
  TextField,
  InputAdornment,
  Tabs,
  Tab,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import MeditationCard from '../components/MeditationCard';
import MeditationPlayer from '../components/MeditationPlayer';

// Временные данные для демонстрации
const DEMO_MEDITATIONS = [
  {
    id: 1,
    title: 'Утренняя медитация',
    description: 'Начните свой день с позитивного настроя и ясности ума. Эта медитация поможет вам настроиться на продуктивный день.',
    duration: 10,
    image: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=500&q=60',
    category: 'Утро',
    isPremium: false,
    videoId: 'dQw4w9WgXcQ', // Замените на реальный ID вашего видео
  },
  {
    id: 2,
    title: 'Глубокое расслабление',
    description: 'Снимите напряжение и стресс с помощью техник глубокого расслабления. Идеально подходит для вечернего времени.',
    duration: 15,
    image: 'https://images.unsplash.com/photo-1528715471579-d1bcf0ba5e83?auto=format&fit=crop&w=500&q=60',
    category: 'Расслабление',
    isPremium: true,
    videoId: 'dQw4w9WgXcQ', // Замените на реальный ID вашего видео
  },
  {
    id: 3,
    title: 'Медитация осознанности',
    description: 'Практика осознанности поможет вам быть более присутствующим в настоящем моменте и улучшит концентрацию.',
    duration: 12,
    image: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=500&q=60',
    category: 'Осознанность',
    isPremium: false,
    videoId: 'dQw4w9WgXcQ', // Замените на реальный ID вашего видео
  },
  {
    id: 4,
    title: 'Сон и восстановление',
    description: 'Эта медитация поможет вам расслабиться перед сном и обеспечит качественный отдых.',
    duration: 20,
    image: 'https://images.unsplash.com/photo-1515894203077-2ce86d11e840?auto=format&fit=crop&w=500&q=60',
    category: 'Сон',
    isPremium: true,
    videoId: 'dQw4w9WgXcQ', // Замените на реальный ID вашего видео
  },
];

const categories = ['Все', 'Утро', 'День', 'Вечер', 'Сон', 'Осознанность', 'Расслабление'];

const Meditation: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(0);
  const [selectedMeditation, setSelectedMeditation] = useState<typeof DEMO_MEDITATIONS[0] | null>(null);

  const handlePlayMeditation = (meditation: typeof DEMO_MEDITATIONS[0]) => {
    setSelectedMeditation(meditation);
  };

  const handleBack = () => {
    setSelectedMeditation(null);
  };

  const filteredMeditations = DEMO_MEDITATIONS.filter(meditation => {
    const matchesSearch = meditation.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         meditation.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 0 || meditation.category === categories[selectedCategory];
    return matchesSearch && matchesCategory;
  });

  if (selectedMeditation) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <MeditationPlayer
          videoId={selectedMeditation.videoId}
          title={selectedMeditation.title}
          description={selectedMeditation.description}
          image={selectedMeditation.image}
          isPremium={selectedMeditation.isPremium}
          onBack={handleBack}
        />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Медитации
      </Typography>
      
      {/* Поиск */}
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Поиск медитаций..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 3 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search />
            </InputAdornment>
          ),
        }}
      />

      {/* Категории */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={selectedCategory}
          onChange={(_, newValue) => setSelectedCategory(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          aria-label="meditation categories"
        >
          {categories.map((category, index) => (
            <Tab key={category} label={category} />
          ))}
        </Tabs>
      </Box>

      {/* Список медитаций */}
      <Grid container spacing={3}>
        {filteredMeditations.map((meditation) => (
          <Grid item xs={12} sm={6} md={4} key={meditation.id}>
            <MeditationCard
              title={meditation.title}
              description={meditation.description}
              duration={meditation.duration}
              image={meditation.image}
              category={meditation.category}
              isPremium={meditation.isPremium}
              onPlay={() => handlePlayMeditation(meditation)}
            />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Meditation; 