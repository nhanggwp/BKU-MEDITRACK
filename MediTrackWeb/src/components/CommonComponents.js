import React, { useState } from 'react';

const LoadingSpinner = ({ size = 'medium', color = '#007bff' }) => {
  const sizeMap = {
    small: '20px',
    medium: '40px',
    large: '60px'
  };

  const spinnerStyle = {
    width: sizeMap[size],
    height: sizeMap[size],
    border: `3px solid #f3f3f3`,
    borderTop: `3px solid ${color}`,
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: 'auto'
  };

  return (
    <>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      <div style={spinnerStyle}></div>
    </>
  );
};

const Toast = ({ message, type = 'info', onClose, duration = 3000 }) => {
  React.useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  const getTypeColor = () => {
    switch (type) {
      case 'success': return '#28a745';
      case 'error': return '#dc3545';
      case 'warning': return '#ffc107';
      default: return '#17a2b8';
    }
  };

  const toastStyle = {
    position: 'fixed',
    top: '20px',
    right: '20px',
    padding: '12px 20px',
    borderRadius: '4px',
    color: 'white',
    backgroundColor: getTypeColor(),
    zIndex: 1000,
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    cursor: 'pointer'
  };

  return (
    <div style={toastStyle} onClick={onClose}>
      {message}
    </div>
  );
};

const ErrorBoundary = ({ children, fallback }) => {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    const handleError = (error) => {
      setHasError(true);
      setError(error);
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleError);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleError);
    };
  }, []);

  if (hasError) {
    return fallback || (
      <div style={{
        padding: '20px',
        textAlign: 'center',
        color: '#dc3545'
      }}>
        <h2>Something went wrong</h2>
        <p>{error?.message || 'An unexpected error occurred'}</p>
        <button 
          onClick={() => {
            setHasError(false);
            setError(null);
          }}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  return children;
};

const Modal = ({ isOpen, onClose, title, children, size = 'medium' }) => {
  if (!isOpen) return null;

  const sizeMap = {
    small: '400px',
    medium: '600px',
    large: '800px'
  };

  const overlayStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  };

  const modalStyle = {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '20px',
    maxWidth: sizeMap[size],
    width: '90%',
    maxHeight: '80vh',
    overflow: 'auto'
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    borderBottom: '1px solid #eee',
    paddingBottom: '10px'
  };

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <h3 style={{ margin: 0 }}>{title}</h3>
          <button 
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '20px',
              cursor: 'pointer'
            }}
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

export { LoadingSpinner, Toast, ErrorBoundary, Modal };
