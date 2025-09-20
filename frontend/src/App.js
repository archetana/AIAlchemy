import React from 'react';

function App() {
  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ color: '#2563eb', marginBottom: '10px' }}>
          🚀 AIAlchemy
        </h1>
        <p style={{ color: '#6b7280', fontSize: '18px' }}>
          AI-Powered Startup Evaluation Platform
        </p>
      </header>
      
      <div style={{ 
        display: 'grid', 
        gap: '20px', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        marginBottom: '30px'
      }}>
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#f0fdf4', 
          borderRadius: '8px',
          border: '1px solid #bbf7d0'
        }}>
          <h3 style={{ color: '#166534', marginTop: '0' }}>✅ Deployment Status</h3>
          <p>✅ Frontend: Running on Cloud Run</p>
          <p>✅ Backend: API operational</p>
          <p>✅ CI/CD: GitHub Actions working</p>
          <p>✅ Infrastructure: Ready for scale</p>
        </div>

        <div style={{ 
          padding: '20px', 
          backgroundColor: '#fefce8', 
          borderRadius: '8px',
          border: '1px solid #fde047'
        }}>
          <h3 style={{ color: '#a16207', marginTop: '0' }}>🛠️ Development Ready</h3>
          <p>📦 Clean codebase prepared</p>
          <p>🔄 Hot reload configured</p>
          <p>📊 Monitoring setup ready</p>
          <p>🚀 Ready for rapid development</p>
        </div>
      </div>
      
      <div style={{ 
        padding: '25px', 
        backgroundColor: '#f8fafc', 
        borderRadius: '8px',
        border: '1px solid #e2e8f0'
      }}>
        <h3 style={{ color: '#334155', marginTop: '0' }}>🎯 Ready to Build Amazing Features</h3>
        <p style={{ marginBottom: '20px' }}>
          The foundation is solid. Time to create the AI-powered startup evaluation platform!
        </p>
        
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <span style={{ 
            padding: '5px 12px', 
            backgroundColor: '#dbeafe', 
            color: '#1e40af',
            borderRadius: '20px',
            fontSize: '14px'
          }}>Material-UI Ready</span>
          <span style={{ 
            padding: '5px 12px', 
            backgroundColor: '#dcfce7', 
            color: '#166534',
            borderRadius: '20px',
            fontSize: '14px'
          }}>FastAPI Backend</span>
          <span style={{ 
            padding: '5px 12px', 
            backgroundColor: '#fef3c7', 
            color: '#a16207',
            borderRadius: '20px',
            fontSize: '14px'
          }}>Cloud Deployed</span>
          <span style={{ 
            padding: '5px 12px', 
            backgroundColor: '#f3e8ff', 
            color: '#7c3aed',
            borderRadius: '20px',
            fontSize: '14px'
          }}>AI Ready</span>
        </div>
      </div>
    </div>
  );
}

export default App;