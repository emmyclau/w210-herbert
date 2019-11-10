from herbert import db


class HerbCondIndex(db.Model):
    '''key, herb_key, condition_key'''

    __tablename__ = 'herbcondix'

    key = db.Column(db.Integer, primary_key=True)
    herb_key = db.Column(db.Integer)
    condition_key = db.Column(db.Integer)

    def __repr__(self):
        return f'<Herb-Cond| {self.key} herb_id: {self.herb_key} cond_id: {self.condition_key}>'