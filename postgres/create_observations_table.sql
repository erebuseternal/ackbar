CREATE TABLE uploads (
    project VARCHAR(16) NOT NULL,
	upload_id INTEGER NOT NULL,
	observation_time TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (project, upload_id)
)