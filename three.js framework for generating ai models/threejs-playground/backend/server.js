// server/server.js
const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS if needed (optional since frontend is served from the same server)
app.use(cors());

// Serve static files from the React app
app.use(express.static(path.join(__dirname, '../client/build')));

// API endpoint to handle any backend logic (optional)
// Example:
// app.get('/api/hello', (req, res) => {
//   res.json({ message: 'Hello from server!' });
// });

// Serve React's index.html for any unknown routes (for client-side routing)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
