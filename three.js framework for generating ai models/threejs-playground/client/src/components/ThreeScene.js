// src/components/ThreeScene.js
import React, { useRef, useEffect, useState } from 'react';
import './ThreeScene.css';

function ThreeScene({ code }) {
  const iframeRef = useRef(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const iframe = iframeRef.current;

    const sendCodeToIframe = () => {
      if (code && iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage({ type: 'executeCode', code }, '*');
      }
    };

    sendCodeToIframe();
  }, [code]);

  useEffect(() => {
    const handleMessage = (event) => {
      // Ensure the message is from the iframe
      if (event.source !== iframeRef.current.contentWindow) return;

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
      <iframe
        ref={iframeRef}
        title="Three.js Sandbox"
        src="/iframe.html"
        sandbox="allow-scripts"
        style={{ width: '100%', height: '100%', border: 'none' }}
      ></iframe>
      {message && <div className="message">{message}</div>}
    </div>
  );
}

export default ThreeScene;
