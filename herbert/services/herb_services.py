from sqlalchemy.orm import joinedload
from herbert.data.herb import Herb


def get_first_herbs(search_term):
    'Searches for a term in the herb name column'
    search_term = f'%{search_term}%'
    results = Herb.query.options(joinedload('source_name')).filter(
        Herb.name.ilike(search_term)).all()
    print([result.source_name.name for result in results])
    return results