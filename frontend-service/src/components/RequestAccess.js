import React from 'react';
import './RequestAccess.css';

function RequestAccess({ email }) {
  return (
    <div className="request-access-container">
      <div className="request-access-card">
        <div className="request-access-icon">📋</div>

        <h1>Access Request Pending</h1>

        <div className="request-access-content">
          <p className="email-display">
            Account: <strong>{email || 'Unknown'}</strong>
          </p>

          <div className="status-box">
            <div className="status-badge pending">Pending Approval</div>
            <p className="status-message">
              Your account has been registered but requires admin approval before you can access the platform.
            </p>
          </div>

          <div className="next-steps">
            <h3>What happens next?</h3>
            <ol>
              <li>We've sent your registration to the admin</li>
              <li>The admin will review your request</li>
              <li>You'll be notified once approved</li>
              <li>You can then configure your API keys and access the dashboard</li>
            </ol>
          </div>

          <div className="info-box">
            <p>
              <strong>Need to speed up?</strong> Contact the platform administrator to request approval.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={() => window.location.reload()}
          >
            Check Status
          </button>
        </div>

        <div className="request-access-footer">
          <small>Registered: {new Date().toLocaleString()}</small>
        </div>
      </div>
    </div>
  );
}

export default RequestAccess;
