-- SQLite
SELECT tipo, SUM(idas) FROM active_places WHERE users_id=1 GROUP BY tipo