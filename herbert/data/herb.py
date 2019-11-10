from herbert import db
from herbert.data.source import Source


class Herb(db.Model):
    '''key, name, chinese_name, source'''

    __tablename__ = 'herb'

    key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    chinese_name = db.Column(db.String)

    source = db.Column(db.Integer, db.ForeignKey('source.key'), nullable=False)

    source_name = db.relationship('Source',
                                  backref=db.backref('herbs', lazy=True))

    def __repr__(self):
        return f'<Herb| {self.name} id: {self.key}>'