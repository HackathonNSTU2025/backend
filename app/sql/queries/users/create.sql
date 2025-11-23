INSERT INTO users (email, username, password, image)
VALUES ($1, $2, $3, $4)
RETURNING *
