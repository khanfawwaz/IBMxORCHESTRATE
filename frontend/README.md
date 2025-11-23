# Warehouse AI Assistant (React Version)

This is the modern React version of the Warehouse AI Assistant frontend.

## 🚀 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

### 3. Build for Production
```bash
npm run build
```

The static files will be generated in the `dist` folder.

## 🔧 Configuration

The API URL is configured in `src/App.jsx`:

```javascript
const API_CONFIG = {
  BASE_URL: window.location.hostname === 'localhost' 
    ? 'http://localhost:9000' 
    : 'https://your-production-url.com',
  // ...
};
```

## 📦 Features

- **Modern UI**: Built with React and Vite
- **Icons**: Using `lucide-react` for a premium feel
- **Responsive**: Adapts to different screen sizes
- **Real-time**: Typing indicators and smooth animations
- **Guardrails**: Visual feedback for off-topic queries
- **Markdown Support**: Renders bold text and lists in AI responses

## 🎨 Styling

- Global styles: `src/index.css`
- Component styles: `src/App.css`
