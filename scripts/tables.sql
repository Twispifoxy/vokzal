CREATE TABLE stations (
    station_code SERIAL PRIMARY KEY,      -- код вокзала
    name VARCHAR(255) NOT NULL,           -- наименование
    inn CHAR(10) UNIQUE NOT NULL,         -- инн, уникальный
    address VARCHAR(255) NOT NULL,        -- адрес
    CONSTRAINT check_inn CHECK (char_length(inn) = 10)  -- проверка длины инн(юр. лицо)
);

CREATE TABLE train_types (
    train_type_code SERIAL PRIMARY KEY,   -- код типа поезда
    name VARCHAR(100) NOT NULL            -- наименование типа
);

CREATE TABLE trains (
    train_code SERIAL PRIMARY KEY,        -- код поезда
    station_code INT NOT NULL,            -- код вокзала
    train_type_code INT NOT NULL,         -- код типа поезда
    name VARCHAR(255) NOT NULL,           -- название поезда
    country_of_origin VARCHAR(100) NOT NULL,  -- страна-производитель
    FOREIGN KEY (station_code) REFERENCES stations(station_code) 
        ON DELETE CASCADE,                -- удаление поезда при удалении вокзала
    FOREIGN KEY (train_type_code) REFERENCES train_types(train_type_code)
        ON DELETE RESTRICT                -- запрещаем удаление, если есть поезда с данным типом
);

CREATE TABLE positions (
    position_code SERIAL PRIMARY KEY,     -- код должности
    name VARCHAR(100) NOT NULL            -- наименование должности
);

CREATE TABLE brigades (
    brigade_code SERIAL PRIMARY KEY,      -- код бригады
    name VARCHAR(100) NOT NULL            -- наименование бригады
);

CREATE TABLE staff (
    inn CHAR(12) PRIMARY KEY,             -- инн человека
    fio VARCHAR(255) NOT NULL,            -- фио
    gender CHAR(1) CHECK (gender IN ('M', 'F')), -- пол: M - мужской, F - женский
    age INT CHECK (age > 18),             -- возраст (больше 18 лет)
    experience_years INT CHECK (experience_years >= 0), -- стаж работы
    position_code INT NOT NULL,           -- код должности
    brigade_code INT,                     -- код бригады
    FOREIGN KEY (position_code) REFERENCES positions(position_code)
        ON DELETE RESTRICT,               -- запрещаем удаление должности, если на нее ссылается персонал
    FOREIGN KEY (brigade_code) REFERENCES brigades(brigade_code)
        ON DELETE RESTRICT,               -- запрещаем удаление бригады, если на нее ссылается персонал
    CONSTRAINT check_inn CHECK (char_length(inn) = 12)
);


CREATE TABLE routes (
    route_code SERIAL PRIMARY KEY,        -- код маршрута
    owner_station_code INT NOT NULL,      -- код вокзала владельца
    train_code INT NOT NULL,              -- код поезда
    departure_station_code INT NOT NULL,  -- код вокзала отправления
    arrival_station_code INT NOT NULL,    -- код вокзала прибытия
    departure_time TIMESTAMP NOT NULL,    -- время отправления
    arrival_time TIMESTAMP NOT NULL,      -- время прибытия
    FOREIGN KEY (owner_station_code) REFERENCES stations(station_code)
        ON DELETE CASCADE,                -- удаление маршрута при удалении вокзала-владельца
    FOREIGN KEY (train_code) REFERENCES trains(train_code)
        ON DELETE CASCADE,                -- удаление маршрута при удалении поезда
    FOREIGN KEY (departure_station_code) REFERENCES stations(station_code),
    FOREIGN KEY (arrival_station_code) REFERENCES stations(station_code)
);

CREATE TABLE route_data (
    route_code INT NOT NULL,              -- код маршрута
    stop_number INT NOT NULL,             -- номер остановки
    station_code INT NOT NULL,            -- код вокзала остановки
    arrival_time TIMESTAMP,               -- время прибытия
    departure_time TIMESTAMP,             -- время убытия
    PRIMARY KEY (route_code, stop_number),
    FOREIGN KEY (route_code) REFERENCES routes(route_code)
        ON DELETE CASCADE,                -- удаление остановок при удалении маршрута
    FOREIGN KEY (station_code) REFERENCES stations(station_code)
);

CREATE TABLE route_brigades (
    route_code INT NOT NULL,              -- код маршрута
    brigade_code INT NOT NULL,            -- код бригады
    PRIMARY KEY (route_code, brigade_code),
    FOREIGN KEY (route_code) REFERENCES routes(route_code)
        ON DELETE CASCADE,                -- удаление связи при удалении маршрута
    FOREIGN KEY (brigade_code) REFERENCES brigades(brigade_code)
        ON DELETE RESTRICT                -- запрещаем удаление бригады, если она привязана к маршруту
);

