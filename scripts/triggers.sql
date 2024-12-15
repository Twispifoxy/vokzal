-- Создание триггера
CREATE OR REPLACE FUNCTION insert_station_train() RETURNS TRIGGER AS $$
BEGIN
    -- Вставка данных в таблицу trains
    INSERT INTO trains (station_code, train_type_code, name, country_of_origin)
    SELECT 
        s.station_code, 
        tt.train_type_code, 
        NEW.train_name, 
        NEW.country_of_origin
    FROM 
        stations s
    JOIN 
        train_types tt ON tt.name = NEW.train_type_name
    WHERE 
        s.name = NEW.station_name;

    -- Возвращаем NULL, чтобы не вставлять данные в представление
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Привязываем триггер к таблице
CREATE TRIGGER insert_station_train_trigger
INSTEAD OF INSERT ON station_trains
FOR EACH ROW EXECUTE FUNCTION insert_station_train();


-- Создание триггера
CREATE OR REPLACE FUNCTION insert_route_stops() RETURNS TRIGGER AS $$
BEGIN
    -- Вставляем данные в route_data
    INSERT INTO route_data (route_code, stop_number, station_code, arrival_time, departure_time)
	SELECT 
		NEW.route_code, 
		NEW.stop_number, 
		s.station_code, 
		NEW.arrival_time, 
		NEW.departure_time
    FROM 
        stations s
	WHERE 
        s.name = NEW.station_name;
    
    -- Возвращаем NULL, чтобы не вставлять данные в представление
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Привязываем триггер к таблице
CREATE TRIGGER trigger_insert_route_stops
INSTEAD OF INSERT ON route_stops
FOR EACH ROW EXECUTE FUNCTION insert_route_stops();


-- Создание функции триггера
CREATE OR REPLACE FUNCTION insert_staff_details() RETURNS TRIGGER AS $$
BEGIN
    -- Вставляем данные в таблицу staff
    INSERT INTO staff (inn, fio, age, gender, experience_years, position_code, brigade_code)
    SELECT 
        NEW.inn,                                -- ИНН сотрудника
        NEW.fio,                                -- ФИО сотрудника
        NEW.age,                                -- Возраст
        NEW.gender,                             -- Пол
        NEW.experience_years,                   -- Стаж работы
        p.position_code,                        -- Код должности
        b.brigade_code                          -- Код бригады
    FROM 
        positions p
    LEFT JOIN brigades b ON NEW.brigade_name = b.name
    WHERE p.name = NEW.position_name;
    
    -- Возвращаем NULL, чтобы не вставлять данные в представление
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Привязываем триггер к представлению
CREATE TRIGGER trigger_insert_staff_details
INSTEAD OF INSERT ON staff_details
FOR EACH ROW EXECUTE FUNCTION insert_staff_details();


-- Создание функции триггера
CREATE OR REPLACE FUNCTION insert_brigade_routes() RETURNS TRIGGER AS $$
DECLARE
    catched_brigade_code INT;  -- Переменная для хранения кода бригады
BEGIN
    -- Проверяем, существует ли бригада с таким названием
    SELECT b.brigade_code INTO catched_brigade_code
    FROM brigades b
    WHERE b.name = NEW.brigade_name;

    -- Если бригада не найдена, то добавляем её
    IF NOT FOUND THEN
        -- Вставляем новую бригаду в таблицу brigades
        INSERT INTO brigades (name)
        VALUES (NEW.brigade_name)
        RETURNING brigade_code INTO catched_brigade_code;
    END IF;

    -- Вставляем данные в таблицу route_brigades
    INSERT INTO route_brigades (route_code, brigade_code)
    VALUES (
        NEW.route_code,                -- Код маршрута
        catched_brigade_code           -- Код бригады (полученный или только что вставленный)
    );

    -- Возвращаем NULL, чтобы не вставлять данные в представление
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Привязываем триггер к представлению
CREATE TRIGGER trigger_insert_brigade_routes
INSTEAD OF INSERT ON brigade_routes
FOR EACH ROW EXECUTE FUNCTION insert_brigade_routes();



SELECT * FROM	 information_schema.triggers;