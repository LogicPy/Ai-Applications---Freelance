// src/components/NavigationControls.js

import React from 'react';

const NavigationControls = ({ controls }) => {
  return (
    <div className="navigation-controls">
      <button onClick={() => controls.reset()}>Reset Camera</button>
      <button onClick={() => controls.zoomIn()}>Zoom In</button>
      <button onClick={() => controls.zoomOut()}>Zoom Out</button>
      {/* Add more custom buttons for camera controls */}
    </div>
  );
};

export default NavigationControls;
