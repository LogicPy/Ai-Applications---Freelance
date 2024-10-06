// src/components/ThreeScene.js
import React, { useEffect, useState } from 'react';
import './ThreeScene.css';
import SandboxIframe from './SandboxIframe';

function ThreeScene({ code }) {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleMessage = (event) => {
      // Ensure the message is from the same origin
      if (event.origin !== window.location.origin) return;

      if (event.data.type === 'codeExecution') {
        if (event.data.status === 'success') {
          setMessage('Code executed successfully.');
        } else if (event.data.status === 'error') {
          setMessage(`Error executing code: ${event.data.error}`);
        }
      }
    };

    window.addEventListener('message', handleMessage);

    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return (
    <div className="three-scene">
      <SandboxIframe code={code} />
      {message && <p className="execution-message">{message}</p>}
    </div>
  );
}

export default ThreeScene;
