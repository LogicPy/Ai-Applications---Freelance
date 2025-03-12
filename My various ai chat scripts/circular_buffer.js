// Just include in your server.js file if you're node.js as:
// const CircularBuffer = require('./circular_buffer');

// Enjoy my wonderful, coding, ai friends! :) Let's keep innovating and changing the future with state-less ai models. 

const fs = require('fs');
const path = require('path');

class CircularBuffer {
  constructor(maxSize) {
    this.maxSize = maxSize;
    this.buffer = [];
  }

  add(item) {
    if (this.buffer.length >= this.maxSize) {
      this.buffer.shift(); // Remove the oldest element
    }
    this.buffer.push(item);
  }

  getAll() {
    return this.buffer;
  }

  setBuffer(newBuffer) {
    if (Array.isArray(newBuffer) && newBuffer.length <= this.maxSize) {
      this.buffer = newBuffer;
    } else {
      console.error('Invalid buffer data or exceeds max size.');
    }
  }

  resize(newMaxSize) {
    if (newMaxSize < this.buffer.length) {
      this.buffer = this.buffer.slice(-newMaxSize); // Trim to fit new size
    }
    this.maxSize = newMaxSize;
  }
}

const BUFFER_FILENAME = path.join(__dirname, 'buffer_state.json');

function saveBufferState(bufferInstance) {
  try {
    fs.writeFileSync(BUFFER_FILENAME, JSON.stringify(bufferInstance.getAll()), 'utf8');
    console.log('Buffer state saved.');
  } catch (error) {
    console.error('Error saving buffer state:', error);
  }
}

function loadBufferState(bufferInstance) {
  try {
    if (fs.existsSync(BUFFER_FILENAME)) {
      const data = fs.readFileSync(BUFFER_FILENAME, 'utf8');
      const loadedBuffer = JSON.parse(data);
      bufferInstance.setBuffer(loadedBuffer);
      console.log('Buffer state loaded.');
    } else {
      console.log('No saved buffer found. Starting with an empty buffer.');
    }
  } catch (error) {
    console.error('Error loading buffer state:', error);
  }
}

// Example usage:
const circularBuffer = new CircularBuffer(100);

// Load buffer on startup
loadBufferState(circularBuffer);

// Use the buffer in your application
circularBuffer.add("data_item");

// Save periodically (e.g., every 5 minutes)
setInterval(() => saveBufferState(circularBuffer), 5 * 60 * 1000);

// Save on process exit
process.on('SIGINT', () => {
  console.log('Received SIGINT. Saving buffer state...');
  saveBufferState(circularBuffer);
  process.exit();
});

process.on('exit', () => {
  console.log('Process exiting. Saving buffer state...');
  saveBufferState(circularBuffer);
});