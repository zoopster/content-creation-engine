/**
 * Main App component.
 */

import React from 'react';
import { WizardContainer } from './components/wizard/WizardContainer';

const Header: React.FC = () => (
  <header className="bg-white shadow-sm">
    <div className="max-w-7xl mx-auto px-4 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-800">
              Content Creation Engine
            </h1>
            <p className="text-sm text-gray-500">
              Multi-agent content generation
            </p>
          </div>
        </div>
        <div className="text-sm text-gray-500">v1.0.0</div>
      </div>
    </div>
  </header>
);

const Footer: React.FC = () => (
  <footer className="bg-white border-t mt-auto">
    <div className="max-w-7xl mx-auto px-4 py-4">
      <p className="text-center text-sm text-gray-500">
        Content Creation Engine - Multi-agent system for automated content
        production
      </p>
    </div>
  </footer>
);

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 py-8">
        <WizardContainer />
      </main>
      <Footer />
    </div>
  );
}

export default App;
