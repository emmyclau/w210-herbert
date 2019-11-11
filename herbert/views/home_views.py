from flask import Blueprint, render_template, request, redirect, url_for
from herbert.services.common import common_herbs, common_conditions, get_team
from herbert.services.search import whoosh_search
from herbert import ds
from whoosh.index import open_dir

bp = Blueprint('home', __name__)


@bp.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        query = request.form.get('search_query')
        return redirect(url_for('home.submit', query=query))

    common_herbs_list = common_herbs()

    common_conditions_list = common_conditions()

    example = common_herbs(1)
    example = f'e.g. {example[0]}'

    team = get_team()

    return render_template('index_jinja.html',
                           common_herbs=common_herbs_list,
                           common_conditions=common_conditions_list,
                           example=example,
                           team=team)


@bp.route('/search', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        query = request.form.get('search_query')
    else:
        query = request.args.get('query')
    print(query)

    index_path = 'herbert/index'
    ix = open_dir(index_path)
    whoosh_search(query, ix)

    herb_name = query
    herb = ds.get_herb(herb_name)

    print(f'herb: {herb.__dict__}')

    #print(herb.pinyin_name)

    return render_template('result_jinja.html',
                           query=query,
                           english_name=herb_name,
                           pinyin_name=herb.pinyin_name,
                           intro=herb.intro,
                           conditions=herb.conditions,
                           sideeffects=herb.sideeffects,
                           interactions=herb.interactions,
                           others=herb.others)


# @bp.route('/contact')
# def contact():
#     return render_template('home/contact.html', team=get_team())
