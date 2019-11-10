from herbert import db


class Source(db.Model):
    '''key, name'''

    __tablename__ = 'source'

    key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return f'<Source| {self.name} id: {self.key}>'