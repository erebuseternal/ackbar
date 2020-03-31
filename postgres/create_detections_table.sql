CREATE TABLE detections (
    project VARCHAR(16) NOT NULL,
	upload_id INTEGER NOT NULL,
	observation_time TIMESTAMP WITHOUT TIME ZONE,
	detection_id INTEGER NOT NULL,
	y0 REAL NOT NULL,
	y1 REAL NOT NULL,
	x0 REAL NOT NULL,
	x1 REAL NOT NULL,
	PRIMARY KEY (project, upload_id, detection_id)
)