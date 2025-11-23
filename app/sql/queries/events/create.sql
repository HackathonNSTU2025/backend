INSERT INTO events (title, image)
VALUES ($1, $2)
RETURNING *
