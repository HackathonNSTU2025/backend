INSERT INTO queues (station_id, title)
VALUES ($1, $2)
RETURNING *
