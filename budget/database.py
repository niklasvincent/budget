from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime
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

    def purge_expenses(self):
        nbr_of_purged_expenses = self.session.query(Expense).delete()
        self.session.commit()
        return nbr_of_purged_expenses

    def purge_markers(self):
        nbr_of_purged_markers = self.session.query(Marker).delete()
        self.session.commit()
        return nbr_of_purged_markers

    def add_marker(self, user_id, created_at, success, nbr_of_updates, nbr_of_deletes, nbr_of_conversions, message):
        self.session.add(
            Marker(
                user_id=user_id,
                created_at=created_at,
                success=success,
                nbr_of_updates=nbr_of_updates,
                nbr_of_deletes=nbr_of_deletes,
                nbr_of_conversions=nbr_of_conversions,
                message=message
            )
        )
        self.session.commit()

    def get_last_successful_marker(self, user_id):
        return self.session.query(Marker).filter_by(success=True, user_id=user_id).order_by(
            Marker.created_at.desc()).first()

    def get_last_marker(self, user_id):
        return self.session.query(Marker).filter_by(user_id=user_id).order_by(Marker.created_at.desc()).first()

    def get_last_successful_marker_datetime(self, user_id):
        marker = self.session.query(Marker) \
            .filter_by(success=True, user_id=user_id) \
            .order_by(Marker.created_at.desc()) \
            .first()
        if marker is not None:
            return marker.created_at
        return None

    def get_currency_conversion_rate(self, for_date, from_currency, to_currency):
        currency_conversion = self.session.query(CurrencyConversion) \
            .filter_by(for_date=for_date, from_currency=from_currency, to_currency=to_currency) \
            .first()
        if currency_conversion is not None:
            return currency_conversion.rate

    def add_currency_conversion(self, for_date, from_currency, to_currency, rate):
        currency_conversion = CurrencyConversion(
            for_date=for_date,
            from_currency=from_currency,
            to_currency=to_currency,
            rate=rate
        )
        self.session.add(currency_conversion)
        self.session.commit()
        return currency_conversion

    def get_expenses(self, user_id):
        return self.session.query(Expense).filter_by(user_id=user_id).order_by(
            Expense.created_at.desc()).all()

    def get_expenses_between(self, user_id, start_date, end_date):
        return self.session.query(Expense) \
            .filter_by(user_id=user_id) \
            .filter(Expense.created_at.between(start_date, end_date)) \
            .order_by(Expense.cost.desc(), Expense.created_at.desc()) \
            .all()

    def delete_expense_by_id(self, expense_id):
        self.session.query(Expense).filter_by(id=expense_id).delete()
        self.session.commit()


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    group_id = Column(Integer)
    group = Column(String)
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

    @property
    def category(self):
        return "{}/{}".format(self.parent_category, self.child_category)

    def as_dictionary(self):
        return {
            "id": self.id,
            "group": self.group,
            "created_at": self.created_at.date().isoformat(),
            "description": self.description,
            "child_category": self.child_category,
            "parent_category": self.parent_category,
            "cost": '%.2f' % self.cost
        }


class Marker(Base):
    __tablename__ = 'markers'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    user_id = Column(Integer)
    success = Column(Boolean)
    nbr_of_updates = Column(Integer)
    nbr_of_deletes = Column(Integer)
    nbr_of_conversions = Column(Integer)
    message = Column(String)

    def __repr__(self):
        return """<Marker(id='%s', created_at='%s', user_id='%s',
        success='%s', deletes='%s', updates='%s', currency_conversions='%s', message='%s')>""" % (
            self.id, self.created_at, self.user_id, self.success, self.nbr_of_deletes, self.nbr_of_updates,
            self.nbr_of_conversions, self.message
        )


class CurrencyConversion(Base):
    __tablename__ = 'currency_conversions'

    id = Column(Integer, primary_key=True)
    for_date = Column(Date)
    from_currency = Column(String)
    to_currency = Column(String)
    rate = Column(Float)

    def __repr__(self):
        return "<CurrencyConversion(id='%s', for_date='%s', from_currency='%s', to_currency='%s', rate='%s')>" % (
            self.id, self.for_date, self.from_currency, self.to_currency, self.rate)
