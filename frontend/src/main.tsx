import { StrictMode, Component, ErrorInfo, ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('React crash:', error, info);
  }
  render() {
    if (this.state.error) {
      const err = this.state.error as Error;
      return (
        <div style={{ padding: 40, fontFamily: 'monospace', background: '#0a0a0f', color: '#f87171', minHeight: '100vh' }}>
          <h1 style={{ fontSize: 24, marginBottom: 16 }}>⚠ App Crashed</h1>
          <pre style={{ whiteSpace: 'pre-wrap', background: '#1a1a2e', padding: 20, borderRadius: 8, color: '#fca5a5' }}>
            {err.message}{'\n\n'}{err.stack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);
