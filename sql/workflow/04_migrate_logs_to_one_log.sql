CREATE TABLE wf_work_stage_list (
	id int AUTO_INCREMENT,
	name varchar(100) NOT NULL,
	PRIMARY KEY (id)
);

INSERT INTO wf_work_stage_list (name) VALUES ('dxf_version_control'), ('cut'), ('bend'), ('weld'), 
	('locksmith'), ('locksmith_door'), ('paint'), ('fireclay'), ('glass'), ('quality_control'), ('final_product');

CREATE TABLE wf_order_work_stage (
	id int AUTO_INCREMENT,
	order_id INT DEFAULT NULL,
	work_stage_id INT DEFAULT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE CASCADE,
	FOREIGN KEY (work_stage_id) REFERENCES wf_work_stage_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_work_log (
	id int AUTO_INCREMENT,
	order_work_stage_id INT DEFAULT NULL,
	stage_id INT DEFAULT NULL,
	user_id INT DEFAULT NULL,
	status_id INT DEFAULT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_work_stage_id) REFERENCES wf_order_work_stage (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE SET NULL,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

TRUNCATE TABLE wf_locksmith_log;
DROP TABLE IF EXISTS wf_locksmith_log;
DROP TABLE IF EXISTS wf_stage_semi_finished_list;

CREATE TABLE wf_locksmith_log (
	id int AUTO_INCREMENT,
	order_id INT DEFAULT NULL,
	stage_id INT DEFAULT NULL,
	user_id INT DEFAULT NULL,
	status_id INT DEFAULT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE CASCADE,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE SET NULL,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);