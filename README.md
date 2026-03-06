# Spotify Data Collector

A Python script that collects recently played songs from the Spotify API and stores them in a PostgreSQL database on an hourly schedule.

## Features

- Spotify OAuth Authentication
- Collects recently played songs
- Stores data in PostgreSQL
- Deduplicates songs using timestamps
- Runs automatically using cron

## Tech Stack

- Python
- Spotify Web API
- PostgreSQL
- Raspberry Pi
- Cron scheduling

## How It Works

1. The script authenticates with the Spotify API
2. It requests recently played tracks for a user
3. It checks the latest stored timestamp to avoid duplicates
4. New tracks are inserted into PostgreSQL
5. The script runs hourly using cron

## Setup

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Add environment variables
5. Run the script

## Environment Variables

Create a `.env` file with:
- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET
- DB_HOST
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_PORT

## Scheduling
This project is designed to run automatically every hour using cron on a Raspberry Pi.

Example cron job:

```0 * * * * /path/to/venv/bin/python -m app.calls >> /path/to/cron.log 2>&1```

## Pipeline

Spotify API → Python Script → PostgreSQL Database