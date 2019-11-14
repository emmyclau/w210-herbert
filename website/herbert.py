from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from data_source import DataSource
from search import SearchEngine
import urllib.parse


app = Flask(__name__)
bootstrap = Bootstrap(app)

ds = DataSource()
se = SearchEngine(ds)

@app.route('/', methods=['GET'])
def index():
    return render_template('index_jinja.html')


@app.route('/search', methods=['GET'])
def search():
    
    # get query
    query = request.args.get('query')  
    query = urllib.parse.unquote(query)

    # search result 
    search_result = se.search(query)
   
    if len(search_result) > 0:
        herb = search_result[0]
    else:
        search_result = {}
        herb = {}
    
    return render_template('result_jinja.html', \
                           query=query, \
                           search_result = search_result,
                           english_name=herb.get('english_name', ''), \
                           pinyin_name=herb.get('pinyin_name', ''), \
                           intro=herb.get('intro', ''), \
                           conditions=herb.get('new_conditions'), \
                           sideeffects=herb.get('sideeffects'), \
                           interactions=herb.get('interactions'), 
                           others=herb.get('others', '')
                          )

@app.errorhandler(404)
def not_found(e):
    return render_template('404_jinja.html')



if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=8080, debug=True)
