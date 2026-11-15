import React from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource/roboto-mono/latin-400.css';
import '@fontsource/roboto-mono/cyrillic-400.css';
import '@fontsource/roboto-mono/latin-500.css';
import '@fontsource/roboto-mono/cyrillic-500.css';
import App from './App.jsx';

createRoot(document.getElementById('root')).render(<App />);
