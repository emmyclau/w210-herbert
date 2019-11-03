from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from data_source import DataSource 
import urllib.parse


app = Flask(__name__)
bootstrap = Bootstrap(app)
ds = DataSource()

@app.route('/', methods=['GET'])
def index():
    return render_template('index_jinja.html')


@app.route('/search', methods=['GET'])
def submit():
    
    query = request.args.get('query')  
    #print(query)
    query = urllib.parse.unquote(query)
    #print(query)
    
    herb_name = query
    herb = ds.get_herb(herb_name)
    
    #print(herb.pinyin_name)
    
    return render_template('result_jinja.html', \
                           query=query, \
                           english_name=herb_name, \
                           pinyin_name=herb.pinyin_name, \
                           intro=herb.intro, \
                           conditions=herb.conditions, \
                           sideeffects=herb.sideeffects, \
                           interactions=herb.interactions, 
                           others=herb.others
                          )

@app.errorhandler(404)
def not_found(e):
    return render_template('404_jinja.html')



if __name__ == '__main__': 
    app.run(debug=True)