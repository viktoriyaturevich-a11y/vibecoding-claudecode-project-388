---
name: tracker
description: Обходит заранее заданный список URL товаров и собирает таблицу цен (regular_price, sale_price, promo_code) за один прогон. Запускается одной фразой, например «запусти трекер», без перечисления ссылок.
---

# tracker

## Язык вывода

Всё, что видит пользователь в результате трекера (**итоговая таблица и сообщения в Telegram**), пишется **на английском**. Общение с пользователем в чате и инструкции в этих файлах могут быть на русском.

## Запуск

Одна фраза: **«запусти трекер»**. Список ссылок вводить не нужно: он зашит ниже.

## Список URL (название товара и ссылка)

1. Alterna Caviar Conditioner 8.5oz (Dermstore): https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-conditioner-8.5oz/11524820/
2. Alterna Caviar Hair Masque 183ml (Dermstore): https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-hair-masque-183ml/15463719/
3. Alterna Caviar Shampoo 8.5oz (Dermstore): https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-shampoo-8.5oz/11286094/
4. Alterna Caviar Shampoo (Ulta): https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-shampoo-xlsImpprod540446?sku=2143390
5. Alterna Caviar Conditioner (Ulta): https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-conditioner-xlsImpprod540378?sku=2143392
6. Alterna Caviar Hair Masque (Ulta): https://www.ulta.com/p/caviar-anti-aging-replenishing-moisture-hair-masque-pimprod2046745?sku=2628720
7. Living Proof Perfect Hair Day Shampoo 236ml (Lookfantastic): https://www.lookfantastic.com/p/living-proof-perfect-hair-day-shampoo-236ml/15914075/
8. Living Proof Perfect Hair Day Conditioner 236ml (Lookfantastic): https://www.lookfantastic.com/p/living-proof-perfect-hair-day-conditioner-236ml/15914077/
9. Living Proof Moisture Rescue Mask 236ml (Lookfantastic): https://www.lookfantastic.com/p/living-proof-moisture-rescue-mask-236ml/17616430/

## Сценарий

1. Для **каждого** URL из списка вызови готовый скилл `extract-price` (через Skill) и получи объект по его контракту: `{ status, currency, regular_price, sale_price, promo_code, usd_rate, error }`.
   Логику извлечения цен, поиска промокода и курса здесь не дублируй: она целиком живёт в `extract-price`. Курс одной валюты ищется один раз за прогон: найденный для первого товара Lookfantastic курс передай `extract-price` для остальных товаров в этой валюте.
2. Прогон не прерывается ни на одном товаре: `status: "error"` и `status: "out_of_stock"` записываются как есть, и обход идёт дальше.
3. Добавь к каждому объекту поле `url`. Получится запись прогона одной формы для всех товаров (см. «Сохранение прогона»).
4. **Сравни с предыдущим прогоном** (см. «Сравнение с предыдущим прогоном»).
5. Верни пользователю **одну итоговую таблицу** (см. «Итоговая таблица»).
6. **Отправь сводку в Telegram** (см. «Уведомление в Telegram»).
7. **Сохрани прогон в `tracker-data`** (см. «Сохранение прогона»).

## Цена в долларах

Везде, где нужна цена в долларах (порог, таблица, Telegram), она считается так: цена в валюте страницы × `usd_rate` **текущего** прогона, с округлением до центов (половина вверх). Для одного товара обе цены (до и после) переводятся по одному и тому же курсу, поэтому изменение курса между прогонами не создаёт ложной разницы.

**Цена покупателя** = `sale_price`, если он не `null`, иначе `regular_price`.

## Сравнение с предыдущим прогоном

Выполняется **до** записи нового файла.

1. **Найди предыдущий прогон.** Через GitHub MCP (`get_file_contents`, `owner` = `viktoriyaturevich-a11y`, `repo` = `tracker-data`, `path` = `/`) получи список файлов в корне репозитория. Оставь только имена вида `YYYY-MM-DD.json`.
   Возьми файл с самой поздней датой (это предыдущий прогон) и прочитай его (`get_file_contents`).
   **Повторный запуск в тот же день:** файл за сегодня тоже считается предыдущим прогоном. Свежие цены сравниваются с тем, что сохранено в нём (в том числе если его правили вручную). После сравнения файл за сегодня перезаписывается (см. «Сохранение прогона»).
   **Если подходящих файлов нет, это первый запуск:** сравнивать не с чем, выведи «First run, nothing to compare» и переходи к сохранению.
2. **Старый формат файла.** Файлы, записанные до перехода на числа, хранят цены строками. При чтении приведи их к новой форме:
   - `"$36.00"` → число `36.00`, `currency: "USD"`, `usd_rate: 1`, `status: "ok"`;
   - все три поля `"—"` → `status: "out_of_stock"`;
   - любое поле `"error"` → `status: "error"`;
   - отдельное поле `"—"` → `null`.
   Если в старом файле цена уже в долларах, а в новом прогоне в другой валюте, сравнивай в долларах: старая цена как есть, новая × `usd_rate` текущего прогона.
3. **Рассчитай diff.** Сопоставь товары по `url` и сравни `status`, `regular_price`, `sale_price` и `promo_code`. Цены одного товара сравнивай в валюте страницы, а полученную разницу переводи в доллары по правилу «Цена в долларах».
   - Товары со `status: "error"` в любом из двух прогонов в сравнении не участвуют (отметь их отдельно: `no data`).
   - URL, которого не было в предыдущем прогоне, это новый товар в списке: отметь `new item in list` и не считай его «back in stock».
4. **Примени правила значимости** из файла `KNOWLEDGE.md` (лежит в корне репозитория). Все незначимые изменения отбрось.

## Итоговая таблица

В таблицу попадают только товары со значимыми изменениями и товары с пометкой `no data`. Колонки:

| Product | Regular price | Sale price | Promo code | Result |
|---|---|---|---|---|

- `Product`: название товара из списка выше **в виде ссылки** на его страницу, `[Название](URL)`. Сам URL в ячейке не показывай.
- `Regular price`, `Sale price`: **текущие** цены в долларах в формате `$36.00`. Если валюта страницы не USD, после цены в скобках исходная цена: `$40.67 (£32.00)`. Нет значения: `—`.
- `Promo code`: текущий промокод или `—`.
- `Result`: разница в цене покупателя со стрелкой по правилам `KNOWLEDGE.md` (раздел «Формат результата»): подорожало `↑ $2.00`, подешевело `↓ $0.70`. Для событий без разницы: `back in stock`, `sold out`, `promo code: — → FLASH22`, `no data`.
- Если значимых изменений нет: «No significant changes».
- Первый запуск: полная таблица прогона по всем товарам, в колонке `Result` везде `—`.

Пример:

| Product | Regular price | Sale price | Promo code | Result |
|---|---|---|---|---|
| [Alterna Caviar Conditioner 8.5oz (Dermstore)](https://www.dermstore.com/p/alterna-caviar-anti-aging-replenishing-moisture-conditioner-8.5oz/11524820/) | $36.00 | — | — | ↓ $1.00 |

## Уведомление в Telegram

После вывода таблицы сформируй из списка значимых изменений **короткую человекочитаемую сводку**, одна строка на изменение, и отправь её через `send.py` (лежит в корне репозитория, токен и chat id берёт из переменных `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`):

```bash
python send.py "<сводка>"
```

Правила сводки (сообщение целиком на английском):
- Одна строка на изменение: `<название товара>: $<цена до>/$<цена после>, price down ↓$<разница>` или `price up ↑$<разница>`.
  Пример: `Alterna Caviar Conditioner 8.5oz (Dermstore): $37.00/$36.00, price down ↓$1.00`
- Название: как в списке URL.
- «Цена до» и «цена после»: **цена покупателя** в долларах (см. «Цена в долларах»). Разница по модулю, с двумя знаками после точки. Она всегда совпадает с колонкой `Result` в таблице.
- Скидка появилась: цена до = обычная, цена после = со скидкой, `price down ↓`.
- Скидка закончилась: цена до = со скидкой, цена после = обычная, `price up ↑`.
- Без цены до и после: `back in stock, $<цена>`; `sold out, was $<цена>`; промокод: `promo code FLASH22 added` / `promo code FLASH22 ended` / `promo code changed: OLD → NEW`.
- Если значимых изменений нет, отправь ровно: `No significant price changes`.
- Первый запуск: `First run, nothing to compare`.
- Несколько строк передавай одним сообщением (переводы строк внутри аргумента).
- Успех: в выводе скрипта `Отправлено.`. Если отправка не удалась, не прерывай прогон: сообщи об ошибке и продолжай сохранение.
- Токен и chat id никогда не выводи в ответе и не пиши в файлы репозитория.

Пример сводки:

```
Alterna Caviar Conditioner 8.5oz (Dermstore): $37.00/$36.00, price down ↓$1.00
Living Proof Perfect Hair Day Shampoo 236ml (Lookfantastic): $40.67/$30.50, price down ↓$10.17
```

## Сохранение прогона

Каждый прогон: **один файл** `YYYY-MM-DD.json` (имя = дата прогона) в **корне** репозитория `viktoriyaturevich-a11y/tracker-data`.

1. Файл: массив объектов, по одному на товар, в той же форме, что вернул `extract-price`, плюс `url`. Цены числом в валюте страницы, без знака валюты и без прочерков; нет значения: `null`.

   ```json
   [
     { "url": "https://www.dermstore.com/p/…/11524820/", "status": "ok", "currency": "USD", "regular_price": 36.00, "sale_price": null, "promo_code": null, "usd_rate": 1, "error": null },
     { "url": "https://www.lookfantastic.com/p/…/15914075/", "status": "ok", "currency": "GBP", "regular_price": 32.00, "sale_price": 24.00, "promo_code": "FLASH22", "usd_rate": 1.2710, "error": null },
     { "url": "https://www.ulta.com/p/…?sku=2143390", "status": "out_of_stock", "currency": "USD", "regular_price": null, "sale_price": null, "promo_code": null, "usd_rate": 1, "error": null },
     { "url": "https://www.ulta.com/p/…?sku=2143392", "status": "error", "currency": null, "regular_price": null, "sale_price": null, "promo_code": null, "usd_rate": null, "error": "HTTP 403" }
   ]
   ```

2. Запиши файл **через GitHub MCP** (инструмент `create_or_update_file`: `owner` = `viktoriyaturevich-a11y`, `repo` = `tracker-data`, `path` = `YYYY-MM-DD.json`, `content` = JSON, осмысленное сообщение коммита, например `Прогон трекера YYYY-MM-DD`). Каждая такая запись сразу отдельный коммит.
3. **Не делай** локальный `git clone` / `git commit` / `git push` для этого репозитория: только запись через MCP.
4. Если файл за эту дату уже есть (повторный прогон в тот же день), сначала получи его `sha` (`get_file_contents`) и передай в `create_or_update_file`, чтобы перезаписать файл.
5. Сообщи пользователю имя файла и ссылку на коммит.
