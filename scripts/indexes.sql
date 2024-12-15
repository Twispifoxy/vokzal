-- для поиска по времи отбытия/прибытия и коду станции
CREATE INDEX idx_route_data_station ON route_data (station_code);
CREATE INDEX idx_route_data_arrival_time ON route_data (arrival_time);
CREATE INDEX idx_route_data_departure_time ON route_data (departure_time);

-- для фильтрации по станциям отправления/прибытия
CREATE INDEX idx_route_departure_station ON routes (departure_station_code);
CREATE INDEX idx_route_arrival_station ON routes (arrival_station_code);

-- для поиска по коду станции, должонсти и бригады
CREATE INDEX idx_staff_position ON staff (position_code);
CREATE INDEX idx_staff_brigade ON staff (brigade_code);

-- для поиска по коду станции
CREATE INDEX idx_train_station ON trains (station_code);