// frontend/src/components/CodeDisplay.js

import React, { useEffect } from 'react';
import Prism from 'prismjs';
import 'prismjs/components/prism-javascript'; // Load JavaScript syntax
import 'prismjs/themes/prism.css'; // Import Prism CSS

const CodeDisplay = ({ code }) => {
  useEffect(() => {
    Prism.highlightAll();
  }, [code]);

  return (
    <pre className="code-container">
      <code className="language-javascript">
        {code}
      </code>
    </pre>
  );
};

export default CodeDisplay;
