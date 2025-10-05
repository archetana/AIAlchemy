/**
 * About Dialog Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AboutDialog from './AboutDialog';
import { APP_INFO } from '../../config/version';

// Mock the version config
jest.mock('../../config/version', () => ({
  APP_INFO: {
    name: 'AIAlchemy',
    fullName: 'AIAlchemy - AI Analyst for Startup Evaluation',
    version: '1.0.3.12345678',
    description: 'Test description',
    team: 'AIAlchemy Team',
    credits: [
      'Built with ❤️ by the AIAlchemy Team',
      'Powered by Google Cloud AI Services'
    ],
    buildDate: '2025-01-20T12:00:00.000Z',
    repository: 'https://github.com/archetana/AIAlchemy',
    license: 'MIT License',
    technologies: [
      'React 18+ with Material-UI',
      'FastAPI with Python 3.11+'
    ]
  },
  DEPLOYMENT_INFO: {
    environment: 'test',
    buildNumber: '123',
    commitHash: 'abc12345',
    buildDate: '2025-01-20T12:00:00.000Z',
    deploymentDate: '2025-01-20T12:00:00.000Z'
  }
}));

describe('AboutDialog', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
  });

  test('renders when open is true', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    expect(screen.getByText('About AIAlchemy')).toBeInTheDocument();
    expect(screen.getByText('AI-powered startup evaluation platform')).toBeInTheDocument();
  });

  test('does not render when open is false', () => {
    render(<AboutDialog open={false} onClose={mockOnClose} />);
    
    expect(screen.queryByText('About AIAlchemy')).not.toBeInTheDocument();
  });

  test('displays version information', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    expect(screen.getByText('1.0.3.12345678')).toBeInTheDocument();
    expect(screen.getByText('TEST')).toBeInTheDocument(); // Environment chip
    expect(screen.getByText('#123')).toBeInTheDocument(); // Build number
  });

  test('displays app metadata', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    expect(screen.getByText('Test description')).toBeInTheDocument();
    expect(screen.getByText('Built with ❤️ by the AIAlchemy Team')).toBeInTheDocument();
    expect(screen.getByText('Powered by Google Cloud AI Services')).toBeInTheDocument();
  });

  test('displays technologies', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    expect(screen.getByText('React 18+ with Material-UI')).toBeInTheDocument();
    expect(screen.getByText('FastAPI with Python 3.11+')).toBeInTheDocument();
  });

  test('displays repository link', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    const githubLink = screen.getByText('View on GitHub');
    expect(githubLink).toBeInTheDocument();
    expect(githubLink.closest('a')).toHaveAttribute('href', 'https://github.com/archetana/AIAlchemy');
  });

  test('displays license information', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    expect(screen.getByText('MIT License')).toBeInTheDocument();
    expect(screen.getByText('© 2025 AIAlchemy Team. All rights reserved.')).toBeInTheDocument();
  });

  test('calls onClose when close button is clicked', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('calls onClose when X button is clicked', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    // Find the X button (IconButton with CloseIcon)
    const closeIconButton = screen.getByRole('button', { name: '' }); // IconButton typically has empty aria-label
    fireEvent.click(closeIconButton);
    
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('copy info button is present', () => {
    render(<AboutDialog open={true} onClose={mockOnClose} />);
    
    const copyButton = screen.getByText('Copy Info');
    expect(copyButton).toBeInTheDocument();
  });
});