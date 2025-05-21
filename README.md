# Autonomous Job Matching Agent

An AI-powered agent that regularly scrapes NY job listings from cryptojobslist.com, matches them against your CV, and sends notifications for high-matching opportunities through Telegram.

## Features

- Automatically scrapes crypto/web3 job listings every 4 hours
- Uses AI to match job descriptions against your CV/resume
- Sends notifications for jobs with 80%+ match score via Telegram
- Tracks previously seen jobs to avoid duplicate notifications

## Setup Instructions

### Prerequisites

- Python 3.8+
- A Telegram bot token (create one via [BotFather](https://t.me/botfather))
- An OpenAI API key
- Your CV in text format

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```
   playwright install
   ```

4. Create your environment file:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your credentials:
   - Add your Telegram bot token
   - Add your Telegram chat ID
   - Add your OpenAI API key

6. Create your CV file:
   ```
   cp FULL_CV.txt.example FULL_CV.txt
   ```

7. Edit `FULL_CV.txt` with your actual CV/resume information

### Running the Agent

To start the agent:

```
python job_agent.py
```

The agent will:
1. Run immediately upon starting
2. Continue running in the background, checking for new jobs every 4 hours
3. Send Telegram notifications for high-matching jobs


## Customization

- Adjust the match threshold in `job_agent.py` (default is 80%)
- Modify the job scraping interval (default is 4 hours)
- Edit the notification format in the `send_telegram_notification` function 

## Funding

## ☕ Sponsor Me

If you like this project, consider [buying me OpenAI credits](https://buymeacoffee.com/bonifaciocalindoro)!

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=bonifaciocalindoro&button_colour=FFDD00&font_colour=000000&font_family=Comic&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/bonifaciocalindoro)
