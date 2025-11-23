WITH queue_counts AS (
    SELECT
        q.id,
        q.station_id,
        COUNT(qe.user_id) AS entry_count
    FROM queues q
    JOIN stations s ON q.station_id = s.id
    LEFT JOIN queue_entries qe ON q.id = qe.queue_id
    WHERE s.event_id = 1
    GROUP BY q.id
),
min_count AS (
    SELECT MIN(entry_count) AS min_entries
    FROM queue_counts
)
SELECT q.*
FROM queues q
JOIN queue_counts qc ON q.id = qc.id
JOIN min_count mc ON qc.entry_count = mc.min_entries
LIMIT 1;
