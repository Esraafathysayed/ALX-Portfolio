#!/usr/bin/python3
"""
Postgresql database Class 
"""
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models.user import User
from models.task import Task
import models
from os import getenv

classes = {
    "User": User,
    "Task": Task
}

class PostgresqlDB():
    """interaacts with the PostgreSQL database"""

    __engine = None 
    __session = None 
    
    def __init__(self):
        """Instantiate a DBStorage object"""
        PostgreSQL_USER = getenv('PostgreSQL_USER')
        PostgreSQL_PWD = getenv('PostgreSQL_PWD')
        PostgreSQL_HOST = getenv('PostgreSQL_HOST')
        PostgreSQL_DB = getenv('PostgreSQL_DB')
        PostgreSQL_DB_URL = getenv('PostgreSQL_DB_URL')
        self.__engine = create_engine('postgresql+psycopg2://{}:{}@{}/{}'.format(PostgreSQL_USER,
                                                                                PostgreSQL_PWD,
                                                                                PostgreSQL_HOST,
                                                                                PostgreSQL_DB),
                                                                                echo=False)

    def reload(self):
            """reloads data from the database"""
            Base.metadata.create_all(self.__engine)
            sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
            Session = scoped_session(sess_factory)
            self.__session = Session

    def all(self, cls=None):
        """query on the current database session"""
        new_dict = {}
        for clss in classes:
            if cls is None or cls is classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss]).all()
                for obj in objs:
                    key = obj.id
                    new_dict[key] = obj
        return new_dict

    # def all(self, cls=None):
    #     """query on the current database session"""
    #     new_dict = {}
    #     for clss in classes:
    #         if cls is None or cls is classes[clss] or cls is clss:
    #             objs = self.__session.query(classes[clss]).all()
    #             for obj in objs:
    #                 key = obj.__class__.__name__ + '.' + obj.id
    #                 new_dict[key] = obj
    #     return (new_dict)

    def new(self, obj):
        """add the object to the current database session"""
        self.__session.add(obj)

    def new_all(self, obj):
        """add all objects to the current database session"""
        self.__session.add_all(obj)
    
    def save(self):
        """commit changes to the database"""
        self.__session.commit()

    def delete(self, obj=None):
        """delete from the current database session obj if not None"""
        if obj is not None:
            self.__session.delete(obj)

    def close(self):
        """ close the database session"""
        self.__session.remove()

    # def get(self, cls, id):
    #     """
    #     Returns the object based on the class name and its ID, or
    #     None if not found
    #     """
    #     if cls not in classes.values():
    #         return None

    #     all_cls = models.storage.all(cls)
    #     for value in all_cls.values():
    #         if (value.id == id):
    #             return value

    #     return None

    def get(self, cls, id_or_filter):
        """
        Retrieves one object based on its class and id or a filter.
        :param cls: class of the object to retrieve
        :param id_or_filter: either the id of the object or a dictionary of attributes to filter by
        :return: the object if found, otherwise None
        """
        if isinstance(id_or_filter, dict):
            query = self.__session.query(cls)
            for key, value in id_or_filter.items():
                query = query.filter(getattr(cls, key) == value)
            try:
                return query.one()
            except NoResultFound:
                return None
        else:
            return self.__session.query(cls).get(id_or_filter)

    def count(self, cls=None):
        """
        count the number of objects in storage
        """
        all_class = classes.values()

        if not cls:
            count = 0
            for clas in all_class:
                count += len(models.storage.all(clas).values())
        else:
            count = len(models.storage.all(cls).values())

        return count
