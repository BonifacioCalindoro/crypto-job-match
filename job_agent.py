import asyncio
import schedule
import time
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests
from scraper import scrape_jobs
from openai import OpenAI

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
THRESHOLD = 80

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("job_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def load_cv():
    """Load and parse the CV from FULL_CV.txt"""
    try:
        with open("FULL_CV.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("CV file not found! Please create FULL_CV.txt")
        return None

def load_jobs():
    """Load previously scraped jobs from jobs.json"""
    try:
        with open("jobs.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("No previous jobs file found or invalid JSON")
        return []

def get_new_jobs(previous_jobs, current_jobs):
    """Compare and return only new jobs"""
    prev_titles = {f"{job['title']}_{job['company']}" for job in previous_jobs}
    new_jobs = []
    
    for job in current_jobs:
        job_key = f"{job['title']}_{job['company']}"
        if job_key not in prev_titles:
            new_jobs.append(job)
    
    return new_jobs

def calculate_match_score(cv_text, job_description):
    """Use OpenAI to calculate how well the CV matches the job description"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI career advisor that evaluates job fit. Provide a matching percentage (0-100%) based on how well the candidate's CV matches the job description."},
                {"role": "user", "content": f"Please analyze this job description and CV, and provide a matching percentage (0-100%), followed by a brief reason for your assessment (max 100 words). Job Description: {job_description}\n\nCV: {cv_text}"}
            ],
            temperature=0.2
        )
        
        result = response.choices[0].message.content.strip()
        
        # Extract percentage from the response
        import re
        percentage_match = re.search(r'(\d{1,3})%', result)
        if percentage_match:
            percentage = int(percentage_match.group(1))
            reason = result
            return percentage, reason
        else:
            logger.warning(f"Could not extract percentage from: {result}")
            return 0, "Could not determine match percentage"
    
    except Exception as e:
        logger.error(f"Error calculating match score: {str(e)}")
        return 0, f"Error: {str(e)}"

def send_telegram_notification(job, match_score, match_reason):
    """Send a notification to Telegram with job details and match score"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message = (
        f"🔥 *New Job Match: {match_score}%* 🔥\n\n"
        f"*{job['title']}*\n"
        f"Company: {job['company']}\n"
        f"Salary: {job['salary']}\n"
        f"Location: {job['location']}\n"
        f"Posted: {job['posted']}\n\n"
        f"*Match Analysis:*\n{match_reason}\n\n"
        f"*Description:*\n{job['description'][:300]}...\n\n"
        f"*Tags:* {', '.join(job['tags'])}"
    )
    
    try:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logger.info(f"Notification sent for job: {job['title']}")
            return True
        else:
            logger.error(f"Failed to send notification: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return False

async def process_jobs():
    """Main function to process jobs"""
    logger.info("Starting job processing...")
    
    # Load CV
    cv_text = load_cv()
    if not cv_text:
        return
    
    # Load previous jobs
    previous_jobs = load_jobs()
    
    # Scrape current jobs
    await scrape_jobs()
    
    # Load newly scraped jobs
    current_jobs = load_jobs()
    
    # Get only new jobs
    new_jobs = get_new_jobs(previous_jobs, current_jobs)
    logger.info(f"Found {len(new_jobs)} new jobs")
    
    # Process each new job
    for job in new_jobs:
        # Calculate match score
        match_score, match_reason = calculate_match_score(cv_text, job['description'])
        logger.info(f"Job: {job['title']} - Match Score: {match_score}%")
        
        # Send notification if match score is above threshold
        if match_score >= THRESHOLD:
            send_telegram_notification(job, match_score, match_reason)

def run_job():
    """Run the job process and handle exceptions"""
    try:
        logger.info("Running scheduled job")
        asyncio.run(process_jobs())
        logger.info("Job completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")

def schedule_jobs():
    """Schedule jobs to run every 4 hours"""
    schedule.every(4).hours.do(run_job)
    logger.info("Jobs scheduled to run every 4 hours")
    
    # Run once immediately on startup
    run_job()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute for pending tasks

if __name__ == "__main__":
    logger.info("Starting Job Agent")
    schedule_jobs() 