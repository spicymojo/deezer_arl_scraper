#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN='your_bot_token_here'  # Replace with actual token
export ALLOWED_USERS='allowed_users_here'  # List with users id, [1,2]

echo "Setup complete. You can now run the project using 'python deezer_arl_telegram_bot.py'"