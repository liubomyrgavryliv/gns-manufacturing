ALTER TABLE wf_order_work_stage ADD COLUMN is_locked bool DEFAULT TRUE;
ALTER TABLE wf_order_log ADD COLUMN is_finished bool DEFAULT FALSE;
