create schema meta default character set utf8mb4

CREATE TABLE meta.dc (
    dc_id  INT NOT NULL COMMENT 'concept id',
    dc_table VARCHAR(40) NOT NULL COMMENT 'concept physical name, the value is other table name',
    dc_name VARCHAR(40) NOT NULL COMMENT 'concept logical name'
);

INSERT INTO meta.dc(dc_id, dc_table, dc_name) VALUES (1, 'vendor.dc', 'dc');
INSERT INTO meta.dc(dc_id, dc_table, dc_name) VALUES (2, 'product.dc', 'dc');

CREATE TABLE meta.dca (
    dca_id INT NOT NULL COMMENT 'attribute id',
    dc_id INT NOT NULL COMMENT 'concept id',
    dca_field_name VARCHAR(40) NOT NULL COMMENT 'attribute physical name, the value is other table name',
    dca_name VARCHAR(40) NOT NULL COMMENT 'attribute logical name'
);

INSERT INTO meta.dca(dca_id, dc_id, dca_field_name, dca_name) VALUES (1, 1, 'dca1', 'vendor_dca1');
INSERT INTO meta.dca(dca_id, dc_id, dca_field_name, dca_name) VALUES (2, 1, 'dca2', 'vendor_dca2'),
INSERT INTO meta.dca(dca_id, dc_id, dca_field_name, dca_name) VALUES (3, 2, 'dca1', 'product_dca1'),
INSERT INTO meta.dca(dca_id, dc_id, dca_field_name, dca_name) VALUES (4, 2, 'dca2', 'product_dca2');

CREATE TABLE meta.vin_pin_map (
    vin_dca_id INT NOT NULL COMMENT 'vin concept id',
    pin_dca_id INT NOT NULL COMMENT 'pin concept id'
);

INSERT INTO meta.vin_pin_map(vin_dca_id, pin_dca_id) VALUES (1, 3);
INSERT INTO meta.vin_pin_map(vin_dca_id, pin_dca_id) VALUES (2, 4);

create schema vendor default character set utf8mb4

CREATE TABLE vendor.dc (
    vin INT NOT NULL COMMENT 'vin id',
    dca1 VARCHAR(40) NOT NULL COMMENT 'column name is vin attribute physical name, value is vin attribute value',
    dca2 VARCHAR(40) NOT NULL COMMENT 'column name is vin attribute physical name, value is vin attribute value'
);

INSERT INTO vendor.dc(vin, dca1, dca2) VALUES (1, 'vendor_dca1_value', 'vendor_dca2_value');

create schema product default character set utf8mb4

CREATE TABLE product.dc (
    pin INT NOT NULL,
    dca1 VARCHAR(40) NOT NULL COMMENT 'column name is pin attribute physical name, value is pin attribute value',
    dca2 VARCHAR(40) NOT NULL COMMENT 'column name is pin attribute physical name, value is pin attribute value'
);
