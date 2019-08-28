# E-Scooter OTTO NOW Scraper

Scrapes https://escooter.ottonow.de periodically to detect whether scooters can now be purchased or not. Sends a slack alert as soon as they can be purchased

### Setup
Rename `config.example.json` to `config.json` and fill out Slack Webhook URL. Check Slack API documentation on how to obtain a Slack Services URL for Incoming Webhooks.

### Docker
Build image with `docker build -t escooter-ottonow .`

Run image with `docker run -d escooter-ottonow`

The container will exit as soon as scooters are available and alerts have been sent out.