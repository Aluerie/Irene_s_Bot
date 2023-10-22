CREATE TABLE IF NOT EXISTS joined_streamers (
    user_id BIGINT PRIMARY KEY,
    user_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_commands (
    command_name TEXT NOT NULL,
    content TEXT NOT NULL,
    streamer_id BIGINT NOT NULL,

    PRIMARY KEY (streamer_id, command_name),

    CONSTRAINT fk_streamer
        FOREIGN KEY (streamer_id)
            REFERENCES joined_streamers(user_id) ON DELETE CASCADE
);
