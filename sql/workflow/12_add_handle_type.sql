ALTER TABLE wf_order_log RENAME COLUMN handle_id TO handle_type_id;
RENAME TABLE wf_handle_list TO wf_handle_type_list;
