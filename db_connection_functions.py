from sqlalchemy.orm import sessionmaker
from database_setup import User,Course,SecurityQuestion,Feedback
from sqlalchemy import create_engine

def add_user_to_database(engine, net_id, questions, answers, current_classes, past_classes):
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(net_id=net_id)
    for question, answer in zip(questions, answers):
        security_question = SecurityQuestion(question=question, answer=answer)
        user.questions.append(security_question)

    for course_code in current_classes:
        course = Course(course_code=course_code, course_status='current')
        user.courses.append(course)

    for course_code in past_classes:
        course = Course(course_code=course_code, course_status='past')
        user.courses.append(course)

    session.add(user)
    session.commit()

def start_engine():
    conn_string = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset={encoding}'.format(
        user='morse_coders', 
        password='/TCcKNCzR2k=', 
        host = 'jsedocc7.scrc.nyu.edu', 
        port     = 3306, 
        encoding = 'utf8',
        db = 'morse_coders'
    )    
    engine = create_engine(conn_string)
    
    return engine

def check_user(engine,net_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_user = session.query(User).filter_by(net_id=net_id).first()
    
    return existing_user

def get_user_by_net_id(engine, net_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter_by(net_id=net_id).first()
    if user is not None:
        questions = [question.question for question in user.questions]
        answers = [question.answer for question in user.questions]
        current_classes = [course.course_code for course in user.courses if course.course_status == 'current']
        past_classes = [course.course_code for course in user.courses if course.course_status == 'past']

        return {
            "questions": questions,
            "answers": answers,
            "current_classes": current_classes,
            "past_classes": past_classes,
        }

    return None

def get_matches(engine, net_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter_by(net_id=net_id).first()
    other_users = session.query(User).filter(User.net_id != net_id).all()

    user_current_classes = [course.course_code for course in user.courses if course.course_status == 'current']
    user_past_classes = [course.course_code for course in user.courses if course.course_status == 'past']

    matches = []

    for other_user in other_users:
        other_current_classes = [course.course_code for course in other_user.courses if course.course_status == 'current']
        other_past_classes = [course.course_code for course in other_user.courses if course.course_status == 'past']

        if (
            len(set(user_current_classes) & set(other_past_classes)) > 0
            and len(set(user_past_classes) & set(other_current_classes)) > 0
        ):
            match_data = {
                "net_id": other_user.net_id,
                "current_classes": other_current_classes,
                "past_classes": other_past_classes,
            }
            matches.append(match_data)

    return matches

def add_feedback(feedback,engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    new_feedback = Feedback(feedback=feedback)
    session.add(new_feedback)
    session.commit()
    session.close()
    