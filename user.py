from flask_login import UserMixin

class User(UserMixin):
    
    def __init__(self, user_id, type, fname, lname, password, image_name, wages_hr, status):
        self.id = user_id
        self.type = type
        self.fname = fname
        self.lname = lname
        self.password = password
        self.image_name = image_name
        self.wages_hr = wages_hr
        self.status = status

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True 

    @property
    def is_active(self):
        return True 

    @property
    def is_anonymous(self):
        return False
