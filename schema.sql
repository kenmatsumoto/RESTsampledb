drop table if exists tasks;
create table tasks (
  id integer primary key autoincrement,
  title string not null,
  description string not null
);

drop table if exists tasks_in_json;
create table tasks_in_json (
    id integer primary key autoincrement,
    json json
)