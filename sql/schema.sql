CREATE TABLE IF NOT EXISTS twitch_users (
    user_id BIGINT PRIMARY KEY,
    user_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS twitch_commands (
    cmd_name TEXT NOT NULL,
    cmd_text TEXT NOT NULL,
    user_id BIGINT NOT NULL,

    PRIMARY KEY (user_id, cmd_name),

    CONSTRAINT fk_streamer
        FOREIGN KEY (user_id)
            REFERENCES twitch_users(user_id) ON DELETE CASCADE
);