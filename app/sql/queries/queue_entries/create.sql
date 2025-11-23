INSERT INTO queue_entries (user_id, queue_id)
VALUES ($1, $2)
RETURNING *
