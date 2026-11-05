#!/usr/bin/env python3
"""Отправка сообщения в Telegram.

Использование: python send.py "текст сообщения"

Токен и chat id берутся из переменных окружения TELEGRAM_BOT_TOKEN и
TELEGRAM_CHAT_ID. Если их нет, скрипт читает файл .env рядом с собой.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def load_env_file(path):
    """Подхватывает KEY=VALUE из .env, не перезаписывая уже заданные переменные."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print('Использование: python send.py "текст сообщения"', file=sys.stderr)
        return 2
    text = sys.argv[1]

    load_env_file(Path(__file__).resolve().parent / ".env")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Ошибка: не заданы TELEGRAM_BOT_TOKEN и/или TELEGRAM_CHAT_ID.", file=sys.stderr)
        return 1

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as e:
        # Текст ошибки Telegram не содержит токена, но URL с токеном не печатаем.
        detail = e.read().decode("utf-8", "replace")
        print(f"Ошибка Telegram (HTTP {e.code}): {detail}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"Ошибка сети: {getattr(e, 'reason', e)}", file=sys.stderr)
        return 1

    if not body.get("ok"):
        print(f"Ошибка Telegram: {body}", file=sys.stderr)
        return 1
    print("Отправлено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
