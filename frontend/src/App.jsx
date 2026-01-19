import React, { useState } from 'react';
import ProjectSelection from './components/ProjectSelection';
import ProjectSetup from './components/ProjectSetup';
import Dashboard from './components/Dashboard';
import DataEntry from './components/DataEntry';
import FileUpload from './components/FileUpload';
import ManualEntry from './components/ManualEntry';

function App() {
  const [currentView, setCurrentView] = useState('project-selection');
  const [currentProject, setCurrentProject] = useState(null);

  const handleSelectProject = (projectId, projectName, isNew) => {
    setCurrentProject({ id: projectId, name: projectName });

    if (isNew) {
      setCurrentView('project-setup');
    } else {
      setCurrentView('dashboard');
    }
  };

  const handleProjectSetupComplete = () => {
    setCurrentView('dashboard');
  };

  const handleNavigate = (view) => {
    setCurrentView(view);
  };

  const handleBackToProjects = () => {
    setCurrentProject(null);
    setCurrentView('project-selection');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>💰 Budget Management App</h1>
        <p>Track your finances with AI-powered insights</p>
      </div>

      {currentView === 'project-selection' && (
        <ProjectSelection onSelectProject={handleSelectProject} />
      )}

      {currentView === 'project-setup' && currentProject && (
        <ProjectSetup
          projectId={currentProject.id}
          onComplete={handleProjectSetupComplete}
        />
      )}

      {currentView === 'dashboard' && currentProject && (
        <Dashboard
          projectId={currentProject.id}
          projectName={currentProject.name}
          onNavigate={handleNavigate}
          onBack={handleBackToProjects}
        />
      )}

      {currentView === 'data-entry' && currentProject && (
        <DataEntry
          projectId={currentProject.id}
          onComplete={handleBackToDashboard}
        />
      )}

      {currentView === 'file-upload' && currentProject && (
        <FileUpload
          projectId={currentProject.id}
          onComplete={handleBackToDashboard}
        />
      )}

      {currentView === 'manual-entry' && currentProject && (
        <ManualEntry
          projectId={currentProject.id}
          onComplete={handleBackToDashboard}
        />
      )}

      {currentView === 'edit-categories' && currentProject && (
        <ProjectSetup
          projectId={currentProject.id}
          onComplete={handleBackToDashboard}
        />
      )}
    </div>
  );
}

export default App;
