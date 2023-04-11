from sqlalchemy import create_engine, Column, Integer, String, ForeignKey,Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    net_id = Column(String(7), unique=True)

class SecurityQuestion(Base):
    __tablename__ = 'security_questions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question = Column(String(255))
    answer = Column(String(255))
    user = relationship("User", back_populates="questions")

User.questions = relationship("SecurityQuestion", order_by=SecurityQuestion.id, back_populates="user")

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course_code = Column(String(10))
    course_status = Column(String(10))
    user = relationship("User", back_populates="courses")

User.courses = relationship("Course", order_by=Course.id, back_populates="user")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    feedback = Column(Text, nullable=False)
    
def create_tables(engine):
    Base.metadata.create_all(engine)

def insert_data(engine, user_data):
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    for net_id, data in user_data.items():
        user = session.query(User).filter_by(net_id=net_id).first()

        if user is None:
            user = User(net_id=net_id)

        user.questions = []
        for question, answer in zip(data['questions'], data['answers']):
            security_question = SecurityQuestion(question=question, answer=answer)
            user.questions.append(security_question)

        user.courses = []
        for course_code in data['current_classes']:
            course = Course(course_code=course_code, course_status='current')
            user.courses.append(course)

        for course_code in data['past_classes']:
            course = Course(course_code=course_code, course_status='past')
            user.courses.append(course)

        session.add(user)

    session.commit()


if __name__ == "__main__":
    # Replace the following connection string with your own MySQL connection string
    conn_string = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset={encoding}'.format(
        user='morse_coders', 
        password='/TCcKNCzR2k=', 
        host = 'jsedocc7.scrc.nyu.edu', 
        port     = 3306, 
        encoding = 'utf8',
        db = 'morse_coders'
    )    
    engine = create_engine(conn_string)

    create_tables(engine)

    with open('user_data.json', 'r') as f:
        user_data = json.load(f)

    insert_data(engine, user_data)
