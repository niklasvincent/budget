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

    def add_marker(self, user_id, created_at, success, nbr_of_updates, nbr_of_deletes, message):
        self.session.add(
            Marker(
                user_id=user_id,
                created_at=created_at,
                success=success,
                nbr_of_updates=nbr_of_updates,
                nbr_of_deletes=nbr_of_deletes,
                message=message
            )
        )
        self.session.commit()

    def get_last_successful_marker(self, user_id):
        return self.session.query(Marker).filter_by(success=True, user_id=user_id).order_by(Marker.created_at.desc()).first()

    def get_last_successful_marker_datetime(self, user_id):
        marker = self.session.query(Marker)\
            .filter_by(success=True, user_id=user_id)\
            .order_by(Marker.created_at.desc())\
            .first()
        if marker is not None:
            return marker.created_at
        return None


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
    original_currency = Column(String)
    currency = Column(String)

    def __repr__(self):
        return "<Expense(id='%s', user_id='%s', date='%s', description='%s', category='%s/%s', cost='%s %s')>" % (
            self.id, self.user_id, self.created_at, self.description, self.parent_category,
            self.child_category, self.cost, self.currency)


class Marker(Base):
    __tablename__ = 'markers'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    user_id = Column(Integer)
    success = Column(Boolean)
    nbr_of_updates = Column(Integer)
    nbr_of_deletes = Column(Integer)
    message = Column(String)

    def __repr__(self):
        return "<Marker(id='%s', created_at='%s', user_id='%s', success='%s', deletes='%s', updates='%s', message='%s')>" % (
            self.id, self.created_at, self.user_id, self.success, self.nbr_of_deletes, self.nbr_of_updates, self.message)
