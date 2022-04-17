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

CREATE TABLE wf_quality_control_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_payment_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_bending_station_list (
	id INT AUTO_INCREMENT,
	name VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE wf_welding_station_list (
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

	note TEXT DEFAULT NULL,

    delivery TEXT DEFAULT NULL,
    mobile_number VARCHAR(20) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    payment INT DEFAULT NULL,

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
	FOREIGN KEY (priority_id) REFERENCES wf_priority_list (id) ON DELETE CASCADE
);

CREATE TABLE wf_dfx_version_control_log (
	id int AUTO_INCREMENT,
	order_id INT NOT NULL,
	stage_id INT NOT NULL,
	status_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_cut_log (
	id int AUTO_INCREMENT,
	order_id INT NOT NULL,
	stage_id INT NOT NULL,
	status_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_bend_log (
	id int AUTO_INCREMENT,
	order_id INT NOT NULL,
	stage_id INT NOT NULL,
	machine_id INT NOT NULL,
	status_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (machine_id) REFERENCES wf_bending_station_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_weld_log (
	id int AUTO_INCREMENT,
	order_id INT NOT NULL,
	stage_id INT NOT NULL,
	machine_id INT NOT NULL,
	status_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (machine_id) REFERENCES wf_welding_station_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_locksmith_log (
	id int AUTO_INCREMENT,
	order_id INT NOT NULL,
	stage_id INT NOT NULL,
	status_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_semi_finished_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_glass_log (
	id int AUTO_INCREMENT,
	order_id INT NOT NULL,
	stage_id INT NOT NULL,
	status_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_quality_control_log (
	id int AUTO_INCREMENT,
	order_id INT NOT NULL,
	stage_id INT NOT NULL,
	status_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);

CREATE TABLE wf_final_product_log (
	id int AUTO_INCREMENT,
	order_id INT NOT NULL,
	stage_id INT NOT NULL,
	status_id INT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	FOREIGN KEY (order_id) REFERENCES wf_order_log (id) ON DELETE RESTRICT,
	FOREIGN KEY (stage_id) REFERENCES wf_stage_final_list (id) ON DELETE RESTRICT,
	FOREIGN KEY (status_id) REFERENCES wf_job_status_list (id) ON DELETE RESTRICT
);