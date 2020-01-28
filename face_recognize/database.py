from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
import os

default_db_path = os.path.expanduser("~/.face_recognize")
if not os.path.exists(default_db_path):
    os.makedirs(default_db_path)
eng = create_engine('sqlite:///'+os.path.join(default_db_path, "face_feature.db"))
Session = sessionmaker(bind=eng)

Base = declarative_base()


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class UserFeature(Base):
    __tablename__ = "Feature"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    user_feature = Column(String, nullable=False)
    feature_version = Column(Integer, nullable=False)


Base.metadata.create_all(eng)


def delete_user(name):
    sess = Session()
    user = sess.query(User).filter(User.name == name).first()
    if user is None:
        print("User %s doesn't exists" % name)
        return
    sess.query(UserFeature).filter(UserFeature.id == user.id).delete()
    sess.delete(user)
    try:
        sess.commit()
    except InvalidRequestError as e:
        print(e)
        sess.rollback()


def save_feature(names, features, version, new_user=True):
    sess = Session()

    for name, feature in zip(names, features):
        user_feature = UserFeature()
        user = sess.query(User).filter(User.name == name).first()
        if user is None:
            if new_user:
                user = User(name=name)
                sess.add(user)
                try:
                    sess.commit()
                    print("New user: %s" % name)
                except InvalidRequestError as e:
                    print(e)
                    sess.rollback()
                    continue

            else:
                print("User %s doesn't exists" % name)
                continue

        user_feature.user_id = user.id
        user_feature.user_feature = feature.toByteArray()
        user_feature.feature_version = version
        sess.add(user_feature)
        try:
            sess.commit()
            print("New feature for user: %s" % name)
        except InvalidRequestError as e:
            print(e)
            sess.rollback()

    sess.close()
