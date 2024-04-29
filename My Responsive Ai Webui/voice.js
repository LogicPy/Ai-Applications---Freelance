
const axios = require('axios');

const XI_API_KEY = 'bc3f6fab1c2fb9c92c55ae23a66adadb'; // Replace <xi-api-key> with your actual API key

const fs = require('fs');

//const XI_API_KEY = '<xi-api-key>'; // Replace <xi-api-key> with your actual API key
const VOICE_ID = '5o19E2IY2XgjCMkBvs28'; // Replace <voice-id> with your selected voice ID
const textToSpeak = 'Hi friend. How you be doing today?'; // Text you want to convert to speech

const mysql = require('mysql2');

const db = mysql.createPool({
  host: '109.106.250.148',
  user: 'waynecoo_Ai_framework',
  password: 'asdf123',
  database: 'waynecoo_ai_db'
});

const promisePool = db.promise();


axios.post('https://api.elevenlabs.io/v1/voice-generation/generate-voice', {
  voice_id: VOICE_ID,
  text: textToSpeak
}, {
  responseType: 'arraybuffer',
  headers: {
    'xi-api-key': XI_API_KEY,
    'Content-Type': 'application/json'
  }
})
.then(async response => {
  const filePath = 'output.mp3';
  fs.writeFileSync(filePath, response.data);
  console.log('Audio generated successfully.');
const jsonString = data.toString('utf8'); // Converts buffer to string using UTF-8 encoding
console.log(jsonString);
  // Save details to MySQL
  const [rows, fields] = await promisePool.execute(
    'INSERT INTO voice_generations (voice_id, text, audio_file_path) VALUES (?, ?, ?)',
    [VOICE_ID, textToSpeak, filePath]
  );
  console.log('Saved to DB successfully.');
})
.catch(error => {
  console.error('Error generating audio:', error);
});
axios.get('https://api.elevenlabs.io/v1/voice-generation/generate-voice')
  .then(response => {
    const jsonString = response.data.toString('utf8');
    console.log('JSON String:', jsonString);

    const jsonObject = JSON.parse(jsonString);
    console.log('Parsed JSON Object:', jsonObject);
  })
  .catch(error => {
    console.error('Error processing response:', error);
  });
