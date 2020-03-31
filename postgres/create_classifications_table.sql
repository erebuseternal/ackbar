CREATE TABLE classifications (
	project VARCHAR(16) NOT NULL,
    upload_id INTEGER NOT NULL,
	observation_time TIMESTAMP WITHOUT TIME ZONE,
	detection_id INTEGER NOT NULL,
	class_name VARCHAR(32) NOT NULL,
    validated BOOLEAN,
    c0 VARCHAR(32) NOT NULL,
    c1 VARCHAR(32) NOT NULL,
    c2 VARCHAR(32) NOT NULL,
    c3 VARCHAR(32) NOT NULL,
    c4 VARCHAR(32) NOT NULL,
	PRIMARY KEY (project, upload_id, detection_id)
)