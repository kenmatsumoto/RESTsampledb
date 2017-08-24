drop table if exists tasks;
create table tasks (
  task_id integer primary key autoincrement,
  end_date date not null,
  item string not null,
  status integer default 0 not null,
  create_record_date date default current_timestamp,
  update_record_date date
);