import { Layout } from './components/Layout';
import { useWebSocket } from './hooks/useWebSocket';

export default function App() {
  useWebSocket();

  return <Layout />;
}
