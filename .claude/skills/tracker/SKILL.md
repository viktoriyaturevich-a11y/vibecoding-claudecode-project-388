---
name: tracker
description: Обходит заранее заданный список URL товаров и собирает таблицу цен (regular_price, sale_price, promo_code) за один прогон. Запускается одной фразой, например «запусти трекер», без перечисления ссылок.
---

# tracker

## Запуск

Одна фраза: **«запусти трекер»**. Список ссылок вводить не нужно — он зашит ниже.

## Список URL

1. https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-conditioner-8.5oz/11524820/
2. https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-hair-masque-183ml/15463719/
3. https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-shampoo-8.5oz/11286094/
4. https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-shampoo-xlsImpprod540446?sku=2143390
5. https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-conditioner-xlsImpprod540378?sku=2143392
6. https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-hair-masque-pimprod2046745?sku=2628720
7. https://www.lookfantastic.com/p/living-proof-perfect-hair-day-shampoo-236ml/15914075/
8. https://www.lookfantastic.com/p/living-proof-perfect-hair-day-conditioner-236ml/15914077/
9. https://www.lookfantastic.com/p/living-proof-moisture-rescue-mask-236ml/17616430/

## Сценарий

1. Для **каждого** URL из списка вызови готовый скилл `extract-price` (через Skill) и получи объект `{ regular_price, sale_price, promo_code }`.
   Логику извлечения цен, конвертации в доллары и поиска промокода здесь не дублируй — она целиком живёт в `extract-price`.
2. Если для какого-то URL `extract-price` не смог получить данные, не прерывай прогон: запиши в строку `ошибка` и продолжай со следующим URL.
3. Собери результаты в единую таблицу прогона: **одна строка на товар**, колонки — `url`, `regular_price`, `sale_price`, `promo_code`.
4. Если `sale_price` или `promo_code` равны `null`, в таблице ставь прочерк `—`.
5. Верни таблицу пользователю.
6. **Сохрани прогон в `tracker-data`** (см. раздел ниже).

## Формат таблицы

| url | regular_price | sale_price | promo_code |
|---|---|---|---|
| https://… | $36.00 | — | — |

## Сохранение прогона

Каждый прогон — **один файл** `YYYY-MM-DD.json` (имя — дата прогона) в **корне** репозитория `viktoriyaturevich-a11y/tracker-data`.

1. Преобразуй таблицу прогона в JSON — массив объектов, по одному на товар, значения те же, что в таблице (включая прочерк `—`):

   ```json
   [
     { "url": "https://…", "regular_price": "$36.00", "sale_price": "—", "promo_code": "—" }
   ]
   ```

2. Запиши файл **через GitHub MCP** (инструмент `create_or_update_file`: `owner` = `viktoriyaturevich-a11y`, `repo` = `tracker-data`, `path` = `YYYY-MM-DD.json`, `content` = JSON, осмысленное сообщение коммита, например `Прогон трекера YYYY-MM-DD`). Каждая такая запись — сразу отдельный коммит.
3. **Не делай** локальный `git clone` / `git commit` / `git push` для этого репозитория — только запись через MCP.
4. Если файл за эту дату уже есть (повторный прогон в тот же день), сначала получи его `sha` (`get_file_contents`) и передай в `create_or_update_file`, чтобы перезаписать файл.
5. Сообщи пользователю имя файла и ссылку на коммит.
