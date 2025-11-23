-- Миграции
CREATE TABLE schema_migrations (
    version BIGINT PRIMARY KEY,                     -- Текущая версия
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()   -- Когда была применена
);

-- Пользователи
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                          -- ID
    email TEXT UNIQUE NOT NULL,                     -- Email
    username TEXT NOT NULL,                         -- Username
    password TEXT NOT NULL,                         -- Пароль
    image TEXT NOT NULL,                            -- Адрес аватарки
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()   -- Когда был создан
);

-- Мероприятия
CREATE TABLE events (
    id SERIAL PRIMARY KEY,                          -- ID
    title TEXT NOT NULL,                            -- Название мероприятия
    image TEXT NOT NULL,                            -- Адрес фотографии
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()   -- Когда было создано
);

-- Станции (стойки / точки обслуживания внутри мероприятия)
CREATE TABLE stations (
    id SERIAL PRIMARY KEY,                                              -- ID
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,  -- ID мероприятия, которому принадлежит станция
    title TEXT NOT NULL,                                                -- Название станции
    description TEXT NOT NULL                                           -- Описание станции
);

-- Очереди (разные операторы внутри каждой станции)
CREATE TABLE queues (
    id SERIAL PRIMARY KEY,                                                  -- ID
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,  -- ID станции, которой принадлежит очередь
    title TEXT NOT NULL,                                                    -- Название очереди
    current_position INTEGER NOT NULL DEFAULT 1,                            -- Текущая обслуживаемая позиция

    UNIQUE(station_id, title)
);

-- Записи пользователей в очереди
CREATE TABLE queue_entries (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,    -- ID пользователя
    queue_id INTEGER NOT NULL REFERENCES queues(id) ON DELETE CASCADE,  -- ID занимаемой пользователем очереди
    position INTEGER NOT NULL,                                          -- Позиция пользователя в этой очереди
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),                       -- Когда пользователь занял очередь
    served_at TIMESTAMPTZ,                                              -- Время, когда он был обслужен

    PRIMARY KEY (user_id, queue_id),
    UNIQUE (queue_id, position)
);
