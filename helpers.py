''' This document contains helper functions used by app.py. '''

# this doesn't actually work, but can be useful for debugging
def random_alarm():
    guess = random.randint(1,20)
    row = Input.query.filter(Input.id==guess).first()
    if row.alarm_state==True:
        row.alarm_state = False
    else:
        row.alarm_state = True
    db.session.commit()

def vthresh(age, hr, rr, temp):
    # set alarm state to be false 
    alarm_state = False

    # HEART RATE ONLY
    # if age > 0 days and  < 1 week (0.01917808219)
    if age > 0 and age < 0.01917808219:
        if hr < 100 or hr > 180:
            alarm_state = True
    # if age > 1 wk and    < 1 month (0.08219178082)
    elif age >= 0.01917808219 and age < 0.08219178082:
        if hr < 100 or hr > 180:
            alarm_state = True
    # if age > 1 month (0.08219178083) and < 1 year (2)
    elif age >= 0.08219178082 and age < 2:
        if hr < 90  or hr > 180:
            alarm_state = True
    # if age > 2 years (2) and < 5 years (6)
    elif age >= 2 and age < 6:
        if hr > 140:
            alarm_state = True
    # if age > 6 years (6) and < 12 years (13)
    elif age >= 6  and age < 13:
        if hr > 130:
            alarm_state = True
    # if age > 13 years (13) and < 18 years (19)
    elif age >= 13 and age < 18:
        if hr > 110:
            alarm_state = True

    #  TEMPERATURE ONLY
    # if temp > 101.3 F or  < 96.8 F
    if temp < 36 or temp > 38.5:
        alarm_state = True

    # RESPIRATORY RATE ONLY
    if age < 0.5:
        if rr < 30 or rr > 60:
            alarm_state = True
    elif age >= 0.5 or age < 1:
        if rr < 25 or rr > 45:
            alarm_state = True
    elif age >= 1 or age < 3:
        if rr < 20 or rr > 30:
            alarm_state = True
    elif age >=3 or age < 10:
        if rr < 16 or rr > 24:
            alarm_state = True
    elif age >= 10:
        if rr < 14 or rr > 20:
            alarm_state = True

    return alarm_state
    
