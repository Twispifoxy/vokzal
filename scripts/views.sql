-- Поезда за каждым вокзалом
CREATE VIEW station_trains AS
SELECT 
    s.name AS station_name,           -- Наименование вокзала
    tt.name AS train_type_name,       -- Тип поезда
    t.name AS train_name,             -- Название поезда
    t.country_of_origin               -- Страна-производитель
FROM 
    stations s
JOIN 
    trains t ON s.station_code = t.station_code
JOIN 
    train_types tt ON t.train_type_code = tt.train_type_code;

SELECT * FROM station_trains;


-- Полный список остановок для каждого маршрута
CREATE VIEW route_stops AS
SELECT 
    r.route_code,                         -- Код маршрута
    t.name AS train_name,                 -- Название поезда
    s.name AS station_name,               -- Наименование вокзала
    rd.stop_number,                       -- Номер остановки
    rd.arrival_time,                      -- Время прибытия
    rd.departure_time                     -- Время отправления
FROM 
    route_data rd
JOIN 
    routes r ON rd.route_code = r.route_code
JOIN 
    trains t ON r.train_code = t.train_code
JOIN 
    stations s ON rd.station_code = s.station_code
ORDER BY 
    r.route_code, rd.stop_number;         -- Сортировка по маршруту и порядковому номеру остановки

SELECT * FROM route_stops;


-- Список сотрудников с информацией о бригаде, должности и стаже работы
CREATE VIEW staff_details AS
SELECT 
	s.inn,                               -- ИНН сотрудника (12 символов)
    s.fio,                               -- ФИО сотрудника
    s.age,                               -- Возраст
    s.gender,                            -- Пол
    p.name AS position_name,             -- Должность
    b.name AS brigade_name,              -- Бригада
    s.experience_years                   -- Стаж работы
FROM 
    staff s
LEFT JOIN 
    positions p ON s.position_code = p.position_code
LEFT JOIN 
    brigades b ON s.brigade_code = b.brigade_code;

SELECT * FROM staff_details;


-- Список бригад с информацией о маршрутах
CREATE VIEW brigade_routes AS
SELECT 
    b.name AS brigade_name,              -- Название бригады
    r.route_code,                        -- Код маршрута
    s.name AS owner_station_name,        -- Вокзал-владелец маршрута
    t.name AS train_name                 -- Название поезда
FROM 
    route_brigades rb
JOIN 
    brigades b ON rb.brigade_code = b.brigade_code
JOIN 
    routes r ON rb.route_code = r.route_code
JOIN 
    trains t ON r.train_code = t.train_code
JOIN 
    stations s ON r.owner_station_code = s.station_code;

SELECT * FROM brigade_routes;