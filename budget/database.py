from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Database(object):

    def __init__(self, database_filename, echo=False):
        self.engine = create_engine(database_filename, echo=echo)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # Create tables
    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def add_marker(self, created_at, success, message):
        self.session.add(Marker(created_at=created_at, success=success, message=message))
        self.session.commit()

    def get_last_successful_marker(self):
        return self.session.query(Marker).filter_by(success=True).order_by(Marker.created_at.desc()).first()


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    group_id = Column(Integer)
    created_at = Column(DateTime)
    description = Column(String)
    parent_category = Column(String)
    child_category = Column(String)
    cost = Column(Float)

    def __repr__(self):
        return "<Expense(id='%s', user_id='%s', date='%s', description='%s', category='%s/%s', cost='%s')>" % (
            self.id, self.user_id, self.created_at, self.description, self.parent_category,
            self.child_category, self.cost)


class Marker(Base):
    __tablename__ = 'markers'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    user_id = Column(Integer)
    success = Column(Boolean)
    message = Column(String)

    def __repr__(self):
        return "<Marker(id='%s', timestamp='%s', success='%s', message='%s')>" % (
            self.id, self.timestamp, self.success, self.message)
