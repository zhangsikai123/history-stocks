from sqlalchemy import Integer, Column, String, Float

from skystocks.infra.persistence.database import Base


class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    cn_name = Column(String)
    date = Column(Integer)  # 日期
    open = Column(Float)  # 开盘价
    close = Column(Float)  # 收盘价
    rise = Column(Float)  # 涨跌额
    rise_rate = Column(Float)  # 涨跌率: %
    lowest = Column(Float)  # 最低
    highest = Column(Float)  # 最高
    trading_volume = Column(Float)  # 成交量
    turnover = Column(Float)  # 成交额
    turnover_rate = Column(Float)  # 换手率: %

    def __repr__(self):
        return "{}|{}|{}".format(self.cn_name, self.code, self.date)
