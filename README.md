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

## Pipeline

Spotify API → Python Script → PostgreSQL Database