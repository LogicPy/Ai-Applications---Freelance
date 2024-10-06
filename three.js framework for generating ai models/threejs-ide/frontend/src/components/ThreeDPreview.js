// src/components/ThreeDPreview.js
import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const ThreeDPreview = ({ code }) => {
  const mountRef = useRef(null);
console.log('Executing Three.js Code:', code);

  useEffect(() => {
    // Basic Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    mountRef.current.appendChild(renderer.domElement);

    // Run the generated code to add objects to the scene
    try {
      // eslint-disable-next-line no-new-func
      const executeCode = new Function('THREE', 'scene', 'camera', 'renderer', code);
      executeCode(THREE, scene, camera, renderer);
    } catch (error) {
      console.error('Error executing Three.js code:', error);
    }

    camera.position.z = 5;

    const animate = function () {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };

    animate();

    // Cleanup on unmount
    return () => {
      mountRef.current.removeChild(renderer.domElement);
    };
  }, [code]);

  return <div ref={mountRef} style={{ width: '100%', height: '600px' }} />;
};

export default ThreeDPreview;
