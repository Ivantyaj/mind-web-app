import React from 'react';
import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import Navigation from './components/Navigation';
import { Home, Meditation, Tests, Profile } from './pages';

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready(): void;
        expand(): void;
        close(): void;
      };
    };
  }
}

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
});

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Инициализация Telegram WebApp
    const initTelegramWebApp = () => {
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
      }
      setIsLoading(false);
    };

    // Если скрипт уже загружен
    if (window.Telegram?.WebApp) {
      initTelegramWebApp();
    } else {
      // Если скрипт еще загружается, ждем его
      const checkTelegram = setInterval(() => {
        if (window.Telegram?.WebApp) {
          clearInterval(checkTelegram);
          initTelegramWebApp();
        }
      }, 100);

      // Очистка интервала при размонтировании компонента
      return () => clearInterval(checkTelegram);
    }
  }, []);

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="flex flex-col h-screen bg-gray-100">
          <main className="flex-1 overflow-y-auto pb-16">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/meditation" element={<Meditation />} />
              <Route path="/tests" element={<Tests />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </main>
          <Navigation />
        </div>
      </Router>
    </ThemeProvider>
  );
};

export default App; 