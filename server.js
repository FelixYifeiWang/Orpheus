const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const OpenAI = require('openai');

const app = express();

// Middleware
app.use(bodyParser.json()); // Parse JSON bodies
app.use(express.static(path.join(__dirname, 'public')));

// Store conversation history for each session
const sessionHistory = {};

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// AI Chat endpoint
app.post('/api/chat', async (req, res) => {
    const { userInput, brainState, sessionId } = req.body;

    // Initialize conversation history for the session if it doesn't exist
    if (!sessionHistory[sessionId]) {
        sessionHistory[sessionId] = [
            { role: "system", content: "You are a helpful and kind counselor and chatbuddy. Consider brain states when responding. Your responses should be casual and kind. Also be very concise and short. One sentence per response. Let the conversation be daily, don't centered with the mental data all the time." }
        ];
    }

    // Add user input to the session's conversation history
    sessionHistory[sessionId].push({ role: "user", content: `User's brain state: ${brainState}\nUser's input: ${userInput}` });

    try {
        // Generate AI response
        const completion = await openai.chat.completions.create({
            model: "gpt-4",
            messages: sessionHistory[sessionId],
        });

        const reply = completion.choices[0].message.content;

        // Add AI response to the session's conversation history
        sessionHistory[sessionId].push({ role: "assistant", content: reply });

        res.json({ reply });
    } catch (error) {
        console.error('Error with OpenAI API:', error);
        res.status(500).json({ error: 'Error generating AI response.' });
    }
});

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server started on http://localhost:${PORT}`);
});
