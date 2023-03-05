CREATE TABLE IF NOT EXISTS twitch_commands (
    id SERIAL PRIMARY KEY,
    streamer_id BIGINT NOT NULL,
    command_name TEXT NOT NULL, 
    command_text TEXT NOT NULL
);