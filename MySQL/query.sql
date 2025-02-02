USE vietnam_stock;
DELETE FROM historical_stock_data_one_day;
INSERT INTO historical_stock_data_one_day (`time`, `open`, high, low, `close`, volume, ticker)
SELECT `time`, `open`, high, low, `close`, volume, ticker
FROM historical_stock_data_one_day_hose
UNION ALL
SELECT `time`, `open`, high, low, `close`, volume, ticker
FROM historical_stock_data_one_day_hnx
UNION ALL
SELECT `time`, `open`, high, low, `close`, volume, ticker
FROM historical_stock_data_one_day_upcom;