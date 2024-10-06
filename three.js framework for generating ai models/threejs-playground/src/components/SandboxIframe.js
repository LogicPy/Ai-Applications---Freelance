// src/components/SandboxIframe.js
import React, { useRef, useEffect } from 'react';

function SandboxIframe({ code }) {
  const iframeRef = useRef(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;

    // Write a basic HTML structure to the iframe
    iframeDocument.open();
    iframeDocument.write(`
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <title>Sandbox</title>
        <style>
          body { margin: 0; overflow: hidden; }
          #sandbox-root { width: 100%; height: 100%; }
        </style>
      </head>
      <body>
        <div id="sandbox-root"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
          // Initialize Three.js
          const scene = new THREE.Scene();
          const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
          const renderer = new THREE.WebGLRenderer({ antialias: true });
          renderer.setSize(window.innerWidth, window.innerHeight);
          document.body.appendChild(renderer.domElement);
          camera.position.z = 5;

          // Animation loop
          function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
          }
          animate();

          // Expose scene, camera, and renderer to the global scope
          window.scene = scene;
          window.camera = camera;
          window.renderer = renderer;

          // Listen for messages from the parent
          window.addEventListener('message', (event) => {
            if (event.data.type === 'executeCode') {
              try {
                eval(event.data.code);
                event.source.postMessage({ type: 'codeExecution', status: 'success' }, event.origin);
              } catch (error) {
                event.source.postMessage({ type: 'codeExecution', status: 'error', error: error.message }, event.origin);
              }
            }
          });
        </script>
      </body>
      </html>
    `);
    iframeDocument.close();
  }, []);

  useEffect(() => {
    if (code) {
      const iframe = iframeRef.current;
      // Ensure the iframe is ready before sending the message
      iframe.onload = () => {
        iframe.contentWindow.postMessage({ type: 'executeCode', code }, window.location.origin);
      };
      // In case the iframe is already loaded
      if (iframe.contentWindow) {
        iframe.contentWindow.postMessage({ type: 'executeCode', code }, window.location.origin);
      }
    }
  }, [code]);

  // src/components/SandboxIframe.js
return (
  <iframe
    ref={iframeRef}
    title="Sandbox"
    sandbox="allow-scripts"
    style={{ width: '100%', height: '100%', border: '1px solid #ccc' }} // Visible iframe
  ></iframe>
);

}

export default SandboxIframe;
