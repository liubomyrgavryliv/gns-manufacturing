/** Base list tables **/

CREATE TABLE wf_model_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_job_status_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_configuration_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_fireclay_type_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_frame_type_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_glazing_type_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_priority_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_payment_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);


/** Stage list tables **/

CREATE TABLE wf_stage_list (
	id int AUTO_INCREMENT,
	name varchar(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_stage_semi_finished_list (
	id int AUTO_INCREMENT,
	name varchar(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_stage_final_list (
	id int AUTO_INCREMENT,
	name varchar(100) NOT NULL,
	PRIMARY KEY (id)
);


/** Log tables tables **/

CREATE TABLE wf_order_log (
	id int AUTO_INCREMENT,
	model_id INT NOT NULL,
	configuration_id INT NOT NULL,
	fireclay_type_id INT NOT NULL,
	glazing_type_id INT NOT NULL,
	frame_type_id INT NOT NULL,
	priority_id INT NOT NULL,

    delivery TEXT DEFAULT NULL,
    mobile_number VARCHAR(20) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    payment_id INT NOT NULL,

	start_manufacturing BOOLEAN DEFAULT FALSE,

	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	start_date DATETIME DEFAULT NULL,
	deadline_date DATETIME DEFAULT NULL,

	PRIMARY KEY (id),
	FOREIGN KEY (model_id) REFERENCES wf_model_list (id) ON DELETE CASCADE,
	FOREIGN KEY (configuration_id) REFERENCES wf_configuration_list (id) ON DELETE CASCADE,
	FOREIGN KEY (fireclay_type_id) REFERENCES wf_fireclay_type_list (id) ON DELETE CASCADE,
	FOREIGN KEY (glazing_type_id) REFERENCES wf_glazing_type_list (id) ON DELETE CASCADE,
	FOREIGN KEY (frame_type_id) REFERENCES wf_frame_type_list (id) ON DELETE CASCADE,
	FOREIGN KEY (priority_id) REFERENCES wf_priority_list (id) ON DELETE CASCADE,
	FOREIGN KEY (payment_id) REFERENCES wf_payment_list (id) ON DELETE CASCADE
);

CREATE TABLE wf_dxf_version_control_log (
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

CREATE TABLE wf_cut_log (
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

CREATE TABLE wf_bend_log (
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

CREATE TABLE wf_weld_log (
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

CREATE TABLE wf_locksmith_log (
	id int AUTO_INCREMENT,
	order_id INT DEFAULT NULL,
	stage_id INT DEFAULT NULL,
	user_id INT DEFAULT NULL,
	status_id INT DEFAULT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE CASCADE,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_semi_finished_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE SET NULL,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_glass_log (
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

CREATE TABLE wf_quality_control_log (
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

CREATE TABLE wf_final_product_log (
	id int AUTO_INCREMENT,
	order_id INT DEFAULT NULL,
	stage_id INT DEFAULT NULL,
	user_id INT DEFAULT NULL,
	status_id INT DEFAULT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE CASCADE,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_final_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE SET NULL,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_note_log (
	id int AUTO_INCREMENT,
	order_id INT DEFAULT NULL,
	user_id INT DEFAULT NULL,
	note TEXT DEFAULT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE SET NULL
);

CREATE TABLE wf_user_group_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_auth_user_group (
	id int AUTO_INCREMENT,
	user_id INT DEFAULT NULL,
	group_id INT DEFAULT NULL,
	
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE SET NULL,
	FOREIGN KEY (group_id) REFERENCES wf_user_group_list (id) ON DELETE SET NULL
);


INSERT INTO wf_model_list (name) VALUES ('110x52'), ('110x52O'), ('120х80'), ('120х80O'), ('160х52'), ('160х52O'), ('42х60'), ('42х60O'), ('60х42'), ('60х42O'), 
									('70х52'), ('70х52O'), ('72х48x52'), ('76х62'), ('76х62O'), ('80x52'), ('80x52O'), ('95x52'), ('95x52O');
									
INSERT INTO wf_job_status_list (name) VALUES ('стандартний'), ('переробка');
INSERT INTO wf_configuration_list (name) VALUES ('база'), ('ліва'), ('права'), ('гільйотина');
INSERT INTO wf_fireclay_type_list (name) VALUES ('гладке'), ('ребристе');
INSERT INTO wf_frame_type_list (name) VALUES ('без рамки'), ('з рамкою');
INSERT INTO wf_glazing_type_list (name) VALUES ('одинарне'), ('подвійне');
INSERT INTO wf_priority_list (name) VALUES ('низький'), ('середній'), ('високий');
INSERT INTO wf_payment_list (name) VALUES ('оплачено'), ('не оплачено'), ('відтерміновано');
INSERT INTO wf_stage_list (name) VALUES ('виконано'), ('в роботі');
INSERT INTO wf_stage_semi_finished_list (name) VALUES ('в роботі'), ('на складі'), ('передано на фарбування');
INSERT INTO wf_stage_final_list (name) VALUES ('відправлено'), ('для відправки'), ('на складі'), ('скасовано');
INSERT INTO wf_order_log (model_id, configuration_id, fireclay_type_id, glazing_type_id, frame_type_id, priority_id, payment_id, start_manufacturing) VALUES (1, 1, 2, 1, 1, 1, 1, TRUE);
INSERT INTO wf_order_log (model_id, configuration_id, fireclay_type_id, glazing_type_id, frame_type_id, priority_id, payment_id, start_manufacturing) VALUES (2, 2, 2, 2, 2, 2, 1, TRUE);
INSERT INTO wf_order_log (model_id, configuration_id, fireclay_type_id, glazing_type_id, frame_type_id, priority_id, payment_id) VALUES (2, 3, 1, 1, 1, 2, 2);
INSERT INTO wf_order_log (model_id, configuration_id, fireclay_type_id, glazing_type_id, frame_type_id, priority_id, payment_id) VALUES (3, 4, 1, 2, 2, 1, 2);
INSERT INTO wf_dxf_version_control_log (order_id, stage_id, user_id, status_id) VALUES (1, NULL, NULL, 1);
INSERT INTO wf_dxf_version_control_log (order_id, stage_id, user_id, status_id) VALUES (2, NULL, NULL, 1);
INSERT INTO wf_dxf_version_control_log (order_id, stage_id, user_id, status_id) VALUES (1, 2, 3, 1);
INSERT INTO wf_dxf_version_control_log (order_id, stage_id, user_id, status_id) VALUES (1, 1, 3, 1);
INSERT INTO wf_dxf_version_control_log (order_id, stage_id, user_id, status_id) VALUES (2, 2, 3, 1);
INSERT INTO wf_dxf_version_control_log (order_id, stage_id, user_id, status_id) VALUES (2, 1, 3, 1);

INSERT INTO wf_note_log (order_id, user_id, note) VALUES (1, 1, 'some note 1');
INSERT INTO wf_note_log (order_id, user_id, note) VALUES (1, 1, 'some note 2');
INSERT INTO wf_note_log (order_id, user_id, note) VALUES (1, 1, 'some note 3');
INSERT INTO wf_note_log (order_id, user_id, note) VALUES (1, 1, 'some note 4');


INSERT INTO wf_cut_log (order_id, stage_id, user_id, status_id) VALUES (1, NULL, NULL, 1);

INSERT INTO wf_user_group_list (name) VALUES ('dxf_version_control'), ('cut'), ('bend'), ('weld'), ('locksmith'), ('glass'), ('quality_control'), ('final_product');

-- These queries are executed only where Django Auth tables are created!
-- SET sql_mode = '';
-- INSERT INTO auth_group (name) VALUES ("lead"), ("manager"), ("engineer"), ("employee");
-- INSERT INTO auth_user_groups (user_id, group_id) VALUES (1, 1);
INSERT INTO wf_auth_user_group (user_id, group_id) VALUES (3, 1);
INSERT INTO wf_auth_user_group (user_id, group_id) VALUES (4, 2);
