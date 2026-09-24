import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';

export function App() {
  return (
    <div className="min-h-screen flex flex-col font-sans text-slate-900 selection:bg-orange-200 selection:text-orange-900 overflow-x-hidden app-shell">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-5 sm:py-8 min-w-0">
        <Home />
      </main>

      <Footer />
    </div>
  );
}

export default App;
