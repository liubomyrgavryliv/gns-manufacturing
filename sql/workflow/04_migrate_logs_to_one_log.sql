CREATE TABLE wf_work_stage_list (
	id int AUTO_INCREMENT,
	name varchar(100) NOT NULL,
	description TEXT DEFAULT NULL,
	PRIMARY KEY (id)
);

INSERT INTO wf_work_stage_list (name, description) VALUES ('dxf_version_control', 'Перевірка DXF версій'), ('cut', 'Порізка'), 
	('bend', 'Гнуття'), ('weld', 'Зварювання'), 
	('locksmith', 'Слюсарські роботи'), ('locksmith_door', 'Слюсарські роботи (дверцята)'), ('paint', 'Фарбування'), ('fireclay', 'Шамотування'), 
	('glass', 'Скління'), ('quality_control', 'Контроль якості'), ('final_product', 'Пакування');

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

TRUNCATE TABLE wf_auth_user_group;
ALTER TABLE wf_auth_user_group DROP CONSTRAINT wf_auth_user_group_ibfk_2, 
							   DROP COLUMN group_id,
						       ADD COLUMN work_stage_id int NOT NULL REFERENCES wf_work_stage_list(id) ON UPDATE CASCADE;
DROP TABLE IF EXISTS wf_user_group_list;

INSERT INTO wf_auth_user_group(user_id, work_stage_id) VALUES 
(8, 1),
(8, 10),
(9, 1),
(10, 2),
(11, 3),
(12, 3),
(13, 4),
(14, 4),
(15, 5),
(16, 5),
(17, 5),
(18, 5),
(19, 8),
(20, 9),
(21, 7),
(22, 6),
(23, 11);


