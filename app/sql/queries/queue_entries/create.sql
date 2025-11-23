INSERT INTO queue_entries (user_id, station_id)
VALUES ($1, $2)
RETURNING *
