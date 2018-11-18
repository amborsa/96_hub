''' This document contains helper functions used by app.py. '''

# this doesne't actually work, but can be useful for debugging
def random_alarm():
    guess = random.randint(1,20)
    row = Input.query.filter(Input.id==guess).first()
    if row.alarm_state==True:
        row.alarm_state = False
    else:
        row.alarm_state = True
    db.session.commit()
