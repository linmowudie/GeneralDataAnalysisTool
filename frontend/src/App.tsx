import { Routes, Route } from 'react-router-dom';
import MainPage from './modules/main/MainPage';
import { GlobalStateProvider } from './context/GlobalStateContext';
import './App.css';

function App() {
  return (
    <GlobalStateProvider>
      <div className="app-container">
        <Routes>
          <Route path="/*" element={<MainPage />} />
        </Routes>
      </div>
    </GlobalStateProvider>
  );
}

export default App
