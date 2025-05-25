# Uptime Monitor (DevOps Test Project)

This is a simple uptime monitor built with Python.

## What it does
- Sends HTTP requests to https://google.com every 10 seconds
- Saves the result (status code or error) in `log.txt`
- Runs in a Docker container
- GitHub Actions builds the image on every push

## Run it locally

```bash
docker build -t uptime-monitor .
docker run uptime-monitor
```
