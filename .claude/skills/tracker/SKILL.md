---
name: tracker
description: Обходит заранее заданный список URL товаров и собирает таблицу цен (regular_price, sale_price, promo_code) за один прогон. Запускается одной фразой, например «запусти трекер», без перечисления ссылок.
---

# tracker

## Запуск

Одна фраза: **«запусти трекер»**. Список ссылок вводить не нужно — он зашит ниже.

## Список URL (название товара — ссылка)

1. Alterna Caviar Conditioner 8.5oz (Dermstore) — https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-conditioner-8.5oz/11524820/
2. Alterna Caviar Hair Masque 183ml (Dermstore) — https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-hair-masque-183ml/15463719/
3. Alterna Caviar Shampoo 8.5oz (Dermstore) — https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-shampoo-8.5oz/11286094/
4. Alterna Caviar Shampoo (Ulta) — https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-shampoo-xlsImpprod540446?sku=2143390
5. Alterna Caviar Conditioner (Ulta) — https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-conditioner-xlsImpprod540378?sku=2143392
6. Alterna Caviar Hair Masque (Ulta) — https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-hair-masque-pimprod2046745?sku=2628720
7. Living Proof Perfect Hair Day Shampoo 236ml (Lookfantastic) — https://www.lookfantastic.com/p/living-proof-perfect-hair-day-shampoo-236ml/15914075/
8. Living Proof Perfect Hair Day Conditioner 236ml (Lookfantastic) — https://www.lookfantastic.com/p/living-proof-perfect-hair-day-conditioner-236ml/15914077/
9. Living Proof Moisture Rescue Mask 236ml (Lookfantastic) — https://www.lookfantastic.com/p/living-proof-moisture-rescue-mask-236ml/17616430/

## Сценарий

1. Для **каждого** URL из списка вызови готовый скилл `extract-price` (через Skill) и получи объект `{ regular_price, sale_price, promo_code }`.
   Логику извлечения цен, конвертации в доллары и поиска промокода здесь не дублируй — она целиком живёт в `extract-price`.
2. Если для какого-то URL `extract-price` не смог получить данные из-за сбоя (страница не загрузилась, структура не разобрана), не прерывай прогон: запиши в строку `ошибка` и продолжай со следующим URL.
   Если страница загрузилась, но товара в наличии нет (нет цены, «out of stock») — это не сбой: запиши во все три поля `—`.
3. Собери результаты в единую таблицу прогона: **одна строка на товар**, колонки — `url`, `regular_price`, `sale_price`, `promo_code`.
4. Если `sale_price` или `promo_code` равны `null`, в таблице ставь прочерк `—`.
5. **Сравни с предыдущим прогоном** (см. раздел «Сравнение с предыдущим прогоном»).
6. Верни пользователю **одну итоговую таблицу** (формат — в конце раздела «Сравнение с предыдущим прогоном»).
7. **Сохрани прогон в `tracker-data`** (см. раздел «Сохранение прогона»).

## Сравнение с предыдущим прогоном

Выполняется **до** записи нового файла.

1. **Найди предыдущий прогон.** Через GitHub MCP (`get_file_contents`, `owner` = `viktoriyaturevich-a11y`, `repo` = `tracker-data`, `path` = `/`) получи список файлов в корне репозитория. Оставь только имена вида `YYYY-MM-DD.json` с датой **раньше сегодняшней** (файл за сегодня при повторном прогоне не считается предыдущим).
   Возьми файл с самой поздней датой — это предыдущий прогон — и прочитай его (`get_file_contents`).
   **Если подходящих файлов нет — это первый запуск:** сравнивать не с чем, выведи «Первый запуск, сравнивать не с чем» и переходи к сохранению.
2. **Рассчитай diff.** Сопоставь товары по `url`. Для каждого товара сравни поля `regular_price`, `sale_price` и `promo_code` между предыдущим и текущим прогоном. Результат — список изменений по каждому товару.
   - Строки со значением `ошибка` в любом из прогонов в сравнении не участвуют (отметь их отдельно: «нет данных»).
   - URL, которого не было в предыдущем прогоне, — новый товар в списке; отметь «новый товар в списке» и не считай его «back in stock».
3. **Примени правила значимости** из файла `KNOWLEDGE.md` (лежит рядом с этим файлом). Отбрось все незначимые изменения (колебания цены меньше порога и т. п.).
4. **Выведи одну итоговую таблицу только со значимыми изменениями.** В неё попадают только товары, у которых есть значимое изменение; остальные строки не показывай. Колонки:

   | Товар | Обычная цена | Цена со скидкой | Промокод | Результат |
   |---|---|---|---|---|

   - `Товар` — название товара из списка выше **в виде ссылки** на его страницу: `[Название](URL)`. Сам URL в ячейке не показывай.
   - `Обычная цена`, `Цена со скидкой`, `Промокод` — **текущие** значения из нового прогона (прочерк `—`, если значения нет).
   - `Результат` — только разница в цене со стрелкой по правилам `KNOWLEDGE.md` (раздел «Формат результата»): подорожало — `↑ $2.00`, подешевело — `↓ $0.70`. Для событий без разницы цены (`back in stock`, `sold out`, промокод) — короткая пометка.
   - Если значимых изменений нет — напиши «Значимых изменений нет».
   - Если это первый запуск — выведи полную таблицу прогона, а в колонке `Результат` везде ставь `—`.

   Пример:

   | Товар | Обычная цена | Цена со скидкой | Промокод | Результат |
   |---|---|---|---|---|
   | [Alterna Caviar Conditioner 8.5oz (Dermstore)](https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-conditioner-8.5oz/11524820/) | $36.00 | — | — | ↓ $1.00 |

   Названия колонок в таблице для пользователя — русские; в файле `YYYY-MM-DD.json` остаются технические имена полей (`url`, `regular_price`, `sale_price`, `promo_code`).

## Формат таблицы прогона (для сохранения в файл)

В `tracker-data` сохраняется полная таблица прогона **без** колонки `Результат`:

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
