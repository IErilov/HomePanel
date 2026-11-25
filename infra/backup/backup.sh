set -eu

BACKUP_DIR="/backups"
BACKUP_INTERVAL=2592000  # 30 дней в секундах
RETENTION=172800         # 120 дней в минутах

mkdir -p "$BACKUP_DIR"

echo "HP Backup: проверка резервных копий..."

# Находим последнюю резервную копию
LATEST_BACKUP=$(ls -1t "$BACKUP_DIR"/hp_*.dump 2>/dev/null | head -n 1 || true)

NOW=$(date +%s)
CREATE_BACKUP=0

if [ -z "$LATEST_BACKUP" ]; then
    CREATE_BACKUP=1
else
    LAST_BACKUP_TIME=$(stat -c %Y "$LATEST_BACKUP")
    AGE=$((NOW - LAST_BACKUP_TIME))

    if [ "$AGE" -ge "$BACKUP_INTERVAL" ]; then
        CREATE_BACKUP=1
    fi
fi

# Создание новой копии
if [ "$CREATE_BACKUP" -eq 1 ]; then
    TIMESTAMP=$(date -u +"%Y-%m-%d_%H-%M-%S")

    BACKUP_FILE="$BACKUP_DIR/hp_$TIMESTAMP.dump"
    TEMP_FILE="$BACKUP_FILE.tmp"

    echo "Создание резервной копии..."

    if pg_dump \
        -h "$POSTGRES_HOST" \
        -p "${POSTGRES_PORT:-5432}" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        -Fc \
        -f "$TEMP_FILE"; then

        mv "$TEMP_FILE" "$BACKUP_FILE"
        echo "Backup создан: $BACKUP_FILE"
    else
        rm -f "$TEMP_FILE"
        echo "Ошибка создания backup!"
        exit 1
    fi
else
    echo "Новая копия пока не требуется."
fi

# Удаляем копии старше 120 дней
find "$BACKUP_DIR" \
    -type f \
    -name "hp_*.dump" \
    -mmin +"$RETENTION" \
    -delete

echo "Проверка завершена."