BEGIN WORK;
DROP TABLE IF EXISTS stocks;
CREATE TABLE stocks(
    id BIGINT(20) PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) NOT NULL,
    cn_name VARCHAR(20) CHARACTER SET utf8 NOT NULL,
    date INTEGER NOT NULL, # 20200101
    open FLOAT  NOT NULL,
    close FLOAT  NOT NULL,
    rise FLOAT,
    rise_rate FLOAT,
    lowest FLOAT,
    highest FLOAT,
    trading_volume FLOAT,
    turnover FLOAT,
    turnover_rate FLOAT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_code_date using btree (code, date)
);
COMMIT;
