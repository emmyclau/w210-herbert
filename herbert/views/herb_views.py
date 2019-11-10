from flask import Blueprint
from herbert.services.herb_services import get_first_herbs

bp = Blueprint('herb', __name__, template_folder='templates')


@bp.route('/herb/<search_term>')
def herb_search(search_term):
    herbs = get_first_herbs(search_term)

    if len(herbs) > 0:
        herbs = [f'{herb.name}: {herb.source_name.name}' for herb in herbs]
        herbs_page = '<br/>'.join(herbs)
    else:
        herbs_page = 'None found'

    return herbs_page


@bp.route('/dbtest')
def db_test_all():
    '''Tests Connection to all tables'''
    from herbert.data.condition import Condition
    from herbert.data.herb import Herb
    from herbert.data.herbcondix import HerbCondIndex
    from herbert.data.source import Source

    test_results = []

    tables = [Condition, Herb, HerbCondIndex, Source]
    for table in tables:
        result = table.query.get(1)
        print(type(result))

        test_results.append(str(result.__dict__))

    test_results = '<br/>'.join(test_results)

    return (f'Success! <br/>{test_results}')
