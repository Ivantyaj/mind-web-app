interface WebAppUser {
  id: number;
  is_premium?: boolean;
}

interface WebAppInitData {
  user?: WebAppUser;
}

export const useTelegram = () => {
  const tg = window.Telegram?.WebApp;

  const getUserData = (): WebAppUser | null => {
    try {
      if (!tg?.initDataUnsafe?.user) {
        return null;
      }
      return tg.initDataUnsafe.user as WebAppUser;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  };

  const openPremiumBot = () => {
    if (tg) {
      // Отправляем сообщение боту для открытия меню премиум-подписки
      tg.sendData('open_premium_menu');
    }
  };

  return {
    tg,
    user: getUserData(),
    openPremiumBot,
  };
};

export default useTelegram; 