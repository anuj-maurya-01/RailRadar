import React, { useState, useRef } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [alertCount, setAlertCount] = useState(0);
  const searchInputRef = useRef(null);

  const handleOpenSearch = () => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
      searchInputRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col font-sans text-slate-900 dark:text-slate-100 selection:bg-blue-200 dark:selection:bg-blue-800 selection:text-blue-900 dark:selection:text-blue-100 overflow-x-hidden transition-colors duration-200">
      <Header
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        alertCount={alertCount}
        onOpenSearch={handleOpenSearch}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 min-w-0">
        <Home
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          setAlertCount={setAlertCount}
          searchInputRef={searchInputRef}
        />
      </main>

      <Footer />
    </div>
  );
}

export default App;
