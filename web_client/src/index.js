import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ThemeProvider, createTheme } from '@mui/material';

// Создаем тему с настройками палитры
const theme = createTheme({
  palette: {
    background: {
      default: "#fafafa",
      paper: "#fff"  // Устанавливаем цвет paper
    },
  },
});

// Инициализация корневого рендеринга с использованием createRoot
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
