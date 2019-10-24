import json
import os
import random
import time

import requests
from loguru import logger

SLEEP_INTERVAL_IN_SECONDS = 10
SLEEP_INTERVAL_THRESHOLD = 5

SLACK_CHANNEL_NAME = "e-scooter"
WATCHING_URL = "https://escooter.ottonow.de"
TEXT_TO_VALIDATE = "bleib auf dem Laufenden!"
MINIMUM_TEXT_TO_VALIDATE = "Über OTTO NOW"


def _load_database() -> dict:
    with open('db.json', 'r') as f:
        return json.load(f)


def _load_config() -> dict:
    with open('config.json', 'r') as f:
        return json.load(f)


def is_available() -> bool:
    """check if database knows about availability"""
    # create file if not exists
    if not os.path.isfile("db.json"):
        set_available(False)

    data = _load_database()
    return data["available"]


def set_available(v: bool):
    """set availability status in database"""
    with open('db.json', 'w') as f:
        json.dump({"available": v}, f)


def send_alerts(slack_url, message_content):
    """send alert to slack channel"""
    payload = {
        "channel": "#" + SLACK_CHANNEL_NAME,
        "text": message_content
    }

    success = False

    while not success:
        resp = requests.post(slack_url, json=payload)

        if resp.status_code >= 300:
            logger.error("Something went wrong during sending slack alert! Panic")
        else:
            success = True


if __name__ == '__main__':
    logger.info("Starting eScooter OTTOnow Scraper for {}", WATCHING_URL)

    # Load configuration with alerting urls
    cfg = None
    try:
        cfg = _load_config()
    except FileNotFoundError:
        logger.error("config.json is not present. Make sure to read README on how to get started")
        exit(-1)

    if is_available():
        logger.info("Scooters are already available! Go get one.")
        exit(0)

    send_alerts(slack_url=cfg["url"], message_content=":wave: :eyes: Now watching " + WATCHING_URL + "")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    while True:
        response = requests.get(WATCHING_URL, headers=headers)
        content = response.text

        if response.status_code == 200 and MINIMUM_TEXT_TO_VALIDATE in content:

            if TEXT_TO_VALIDATE in response.text:
                # Not yet available :-(
                pass
            else:
                set_available(True)
                logger.info("E-Scooters can now be purchased")
                send_alerts(slack_url=cfg["url"], message_content="<@channel> E-Scooters are now available at OTTO NOW. Go get one at " + WATCHING_URL)
                exit(0)

        time.sleep(SLEEP_INTERVAL_IN_SECONDS + random.randint(-SLEEP_INTERVAL_THRESHOLD, SLEEP_INTERVAL_THRESHOLD))
