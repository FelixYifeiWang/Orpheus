# Emotion-Enhanced Chatbot Using EEG Signals

## Overview
This project combines EEG-based emotional detection with advanced language models like ChatGPT to create an emotionally aware chatbot. By leveraging EEG data from devices like the Muse 2, the chatbot can identify and respond to users' emotional states in real time, enhancing the naturalness and precision of conversations. This innovative approach bridges the gap between linguistic input and emotional perception, offering potential applications in well-being and mental health support.

## Features
- **Real-Time Emotion Detection:** Uses EEG brainwave data to identify emotional states (neutral, peaceful, anxious) with over 95% accuracy.
- **Emotion-Enhanced Conversations:** Integrates emotional data into ChatGPT responses to provide personalized and empathetic interactions.
- **Multi-Modal Input:** Combines text, voice, and EEG signals to enhance the depth and richness of AI conversations.
- **Usability Tested:** Engaged with 20+ participants to refine emotional accuracy and user experience.

## How It Works
1. **Data Collection:** EEG brainwave data is collected using the Muse 2 device.
2. **Emotion Classification:** A GRU-based neural network processes the data to classify emotions into neutral, peaceful, or anxious states.
3. **Chatbot Integration:** The classified emotion is fed into ChatGPT, influencing its responses to better align with the user's emotional state.
4. **User Interaction:** Users interact with the chatbot via voice or text while wearing the EEG device, experiencing emotionally adaptive conversations.
