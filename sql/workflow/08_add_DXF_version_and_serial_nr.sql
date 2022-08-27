ALTER TABLE order_log ADD COLUMN dxf_version varchar(100) DEFAULT NULL,
                      ADD COLUMN serial_number varchar(100) DEFAULT NULL;
