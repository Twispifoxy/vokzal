-- Заполнение таблицы stations
INSERT INTO stations (name, inn, address)
VALUES 
    ('Вокзал Москва', '1234567890', 'Москва, ул. Ленина, 1'),
    ('Вокзал Санкт-Петербург', '0987654321', 'Санкт-Петербург, Невский пр., 50'),
    ('Вокзал Казань', '1122334455', 'Казань, ул. Баумана, 10');

-- Заполнение таблицы train_types
INSERT INTO train_types (name)
VALUES 
    ('Скоростной'),
    ('Грузовой'),
    ('Пассажирский');

-- Заполнение таблицы trains
INSERT INTO trains (station_code, train_type_code, name, country_of_origin)
VALUES 
    (1, 1, 'Сапсан', 'Россия'),
    (2, 3, 'Невский Экспресс', 'Франция'),
    (3, 2, 'Грузовой 2000', 'Германия');

-- Заполнение таблицы positions
INSERT INTO positions (name)
VALUES 
    ('Машинист'),
    ('Кондуктор'),
    ('Диспетчер');

-- Заполнение таблицы brigades
INSERT INTO brigades (name)
VALUES 
    ('Бригада А'),
    ('Бригада Б'),
    ('Бригада В');

-- Заполнение таблицы staff
INSERT INTO staff (inn, fio, gender, age, experience_years, position_code, brigade_code)
VALUES 
    ('123456789012', 'Иванов Иван Иванович', 'M', 35, 10, 1, 1),
    ('234567890123', 'Петров Петр Петрович', 'M', 40, 15, 2, 2),
    ('345678901234', 'Сидорова Мария Ивановна', 'F', 30, 5, 3, 3);

-- Заполнение таблицы routes
INSERT INTO routes (owner_station_code, train_code, departure_station_code, arrival_station_code, departure_time, arrival_time)
VALUES 
    (1, 1, 1, 2, '2024-11-15 08:00:00', '2024-11-15 12:00:00'),
    (2, 2, 2, 3, '2024-11-15 14:00:00', '2024-11-15 18:00:00'),
    (3, 3, 3, 1, '2024-11-16 10:00:00', '2024-11-16 18:00:00');

-- Заполнение таблицы route_data
INSERT INTO route_data (route_code, stop_number, station_code, arrival_time, departure_time)
VALUES 
    (1, 1, 1, NULL, '2024-11-15 08:00:00'),
    (1, 2, 2, '2024-11-15 12:00:00', NULL),
    (2, 1, 2, NULL, '2024-11-15 14:00:00'),
    (2, 2, 3, '2024-11-15 18:00:00', NULL),
    (3, 1, 3, NULL, '2024-11-16 10:00:00'),
    (3, 2, 1, '2024-11-16 18:00:00', NULL);

-- Заполнение таблицы route_brigades
INSERT INTO route_brigades (route_code, brigade_code)
VALUES 
    (1, 1),
    (2, 2),
    (3, 3);