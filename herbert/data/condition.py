from herbert import db


class Condition(db.Model):
    '''key, name, source'''

    __tablename__ = 'condition'

    key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    source = db.Column(db.String)

    def __repr__(self):
        return f'<Condition| {self.name} id: {self.key}>'
