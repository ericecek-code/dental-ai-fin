import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Results from './pages/Results';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Results />
    </QueryClientProvider>
  );
}

export default App;
