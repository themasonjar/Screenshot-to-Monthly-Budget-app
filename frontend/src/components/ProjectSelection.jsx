import React, { useState, useEffect } from 'react';
import api from '../utils/api';

function ProjectSelection({ onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await api.getProjects();
      setProjects(response.data.projects);
      setLoading(false);
    } catch (err) {
      setError('Failed to load projects');
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    try {
      const response = await api.createProject(newProjectName);
      setNewProjectName('');
      setShowCreateForm(false);
      onSelectProject(response.data.project_id, newProjectName, true);
    } catch (err) {
      setError('Failed to create project');
    }
  };

  if (loading) {
    return <div className="loading">Loading projects...</div>;
  }

  return (
    <div className="card">
      <h2>Budget Projects</h2>
      {error && <div className="error">{error}</div>}

      {!showCreateForm ? (
        <>
          <div className="project-list">
            {projects.map((project) => (
              <div
                key={project.id}
                className="project-card"
                onClick={() => onSelectProject(project.id, project.name, false)}
              >
                <h3>{project.name}</h3>
                <p>Created: {new Date(project.created_at).toLocaleDateString()}</p>
              </div>
            ))}
          </div>

          <button
            className="btn btn-primary"
            onClick={() => setShowCreateForm(true)}
            style={{ marginTop: '20px' }}
          >
            + Create New Project
          </button>
        </>
      ) : (
        <form onSubmit={handleCreateProject}>
          <div className="input-group">
            <label>Project Name</label>
            <input
              type="text"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              placeholder="e.g., 2024 Personal Budget"
              autoFocus
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="submit" className="btn btn-primary">
              Create Project
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowCreateForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default ProjectSelection;
