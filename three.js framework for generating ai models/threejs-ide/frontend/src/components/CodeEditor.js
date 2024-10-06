// frontend/src/components/CodeEditor.js
import React from 'react';
import MonacoEditor from 'react-monaco-editor';

const CodeEditor = ({
  height = '500px',
  language = 'javascript',
  theme = 'vs-dark',
  // ... other default props
  ...rest
}) => {
  return (
    <MonacoEditor
      height={height}
      language={language}
      theme={theme}
      {...rest}
    />
  );
};

export default CodeEditor;
