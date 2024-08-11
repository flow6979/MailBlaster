# EmailBlaster
One click and mails blasts just like owls sent thousand of mails in dursley's house for Harry Potter.

## Services
1. Use google sheet link.
2. Use CSV full of email addresses.
3. Write mail addresses manually.

## How to get thing ready?

1. Start redis -

    `redis-server`

2. Start celery -

    `celery -A utils.celery_config.celery_app worker --loglevel=info`

3. Start Flask Application -

    `flask run`





chmod +x start.sh
./start.sh
