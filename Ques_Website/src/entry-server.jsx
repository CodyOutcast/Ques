import { renderToString } from 'react-dom/server';
import App from './App.jsx';
import './i18n';

export function render() {
  return renderToString(<App />);
}