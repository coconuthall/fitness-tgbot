# Telegram bot for weight tracking

## Project description: 
Originallly this was a task task for 
tech interview and i decided to polish it and publish this project on my github

## Project Requirements
aiogram==2.24
asyncpg==0.27.0
databases==0.7.0
pydantic==1.10.4

Additionally you should run a postgresql database

## Installation and launch
1. Go to the project folder, create and activate virtual environment
```
python3 -m venv env
source env/bin/activate
```
2. Install requirements
```
pip install -r requirements.txt
```
3. Include botconfig.ini in the root folder of the project. Example file is in the repository. You should set your telegram bot token and postgresql database connection string
4. Run bot.py
