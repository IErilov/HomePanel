FROM postgres:16-alpine

WORKDIR /backup

COPY backup.sh /usr/local/bin/backup.sh
COPY crontab /etc/crontabs/root

RUN chmod +x /usr/local/bin/backup.sh

CMD ["sh", "-c", "/usr/local/bin/backup.sh && crond -f -l 2"]