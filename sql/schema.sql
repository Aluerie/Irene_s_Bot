CREATE TABLE IF NOT EXISTS twitch_streamers (
    user_id BIGINT PRIMARY KEY,
    user_name BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS twitch_commands (
    cmd_name TEXT NOT NULL,
    cmd_text TEXT NOT NULL,
    user_id BIGINT NOT NULL,

    PRIMARY KEY (user_id, cmd_text),

    CONSTRAINT fk_streamer
        FOREIGN KEY (user_id)
            REFERENCES twitch_streamers(user_id) ON DELETE CASCADE
);