drop table if exists components;
create table components (
  id integer primary key,
  description string not null,
  product integer references products(id)
);

drop table if exists products;
create table products (
  id integer primary key,
  description string not null
);

drop table if exists users;
create table users (
    id integer primary key,
    email string not null,
    password string not null,
    default_url string not null
);

drop table if exists views;
create table views (
    id integer primary key,
    name string,
    product integer references products(id)
    component integer references components(id)
    user integer references users(id)
);
