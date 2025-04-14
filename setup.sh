#!/bin/bash

# Create a requirements.txt file with all necessary dependencies
cat > requirements.txt << EOL
telebot==4.26.0
groq==0.20.0
gtts==2.5.4
langid==1.1.6
python-dotenv==1.0.0
requests==2.32.3
EOL

# Create a .env file for local testing
cat > .env << EOL
TELEGRAM_BOT_TOKEN=
GROQ_API_KEY=
EOL

# Create a start script that loads environment variables
cat > start.sh << EOL
#!/bin/bash
# Load environment variables from .env file if it exists
if [ -f .env ]; then
  export \$(grep -v '^#' .env | xargs)
fi

# Start the bot
python bot.py
EOL

# Make the start script executable
chmod +x start.sh

echo "Setup complete. You can now run ./start.sh to start the bot locally."
