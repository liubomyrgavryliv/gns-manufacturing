CREATE TABLE wf_order_status_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

INSERT INTO wf_order_status_list (name) VALUES ('В роботі'), ('Виготовлено'), ('Відправлено'), ('Скасовано');

CREATE TABLE wf_order_status (
	id INT AUTO_INCREMENT,
	order_id int NOT NULL,
	order_status_id int NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (order_status_id) REFERENCES wf_order_status_list (id) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO wf_order_status (order_id, order_status_id)
SELECT id AS order_id, 2 AS order_status_id
FROM wf_order_log wol WHERE wol.is_finished ;

INSERT INTO wf_order_status (order_id, order_status_id)
SELECT id AS order_id, 3 AS order_status_id
FROM wf_order_log wol WHERE wol.is_canceled  ;

ALTER TABLE wf_order_log DROP COLUMN is_finished,
                         DROP COLUMN is_canceled;

INSERT INTO wf_work_stage_list (name, description) VALUES ('delivery', 'Відправка');
INSERT INTO wf_auth_user_group (user_id, work_stage_id) VALUES (23, 12);
ALTER TABLE wf_auth_user_group ADD FOREIGN KEY (work_stage_id) REFERENCES wf_work_stage_list(id) ON UPDATE CASCADE ON DELETE CASCADE;
