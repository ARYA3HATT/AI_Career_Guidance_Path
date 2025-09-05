import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
// 1. Import Mantine's CSS styles
import '@mantine/core/styles.css';
// 2. Import the MantineProvider
import { MantineProvider } from '@mantine/core';
// 3. Import our custom CSS file
import './App.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* 4. Wrap your App component with the MantineProvider */}
    <MantineProvider defaultColorScheme="dark">
      <App />
    </MantineProvider>
  </React.StrictMode>,
)

