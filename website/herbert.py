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
    
    if query is None:
        query = ''   
    
    query = urllib.parse.unquote(query)

    # search result 
    search_result = se.search(query)
   

    # no result
    if len(search_result) == 0:
        return render_template('404_jinja.html', query=query)
        
        
        
    
        
    herb = search_result[0]
    print(herb.get('english_name', ''))
    print(herb.get('pinyin_name', ''))
    print(herb.get('intro', ''))
    print(herb.get('new_conditions'))
    print(herb.get('interactions'))
    print(herb.get('safe'))
    print(herb.get('likely_safe'))
    print(herb.get('possibly_safe'))
    print(herb.get('likely_unsafe'))
    print(herb.get('possibly_unsafe'))
      
    
    return render_template('result_jinja.html', \
                           query=query, \
                           search_result = search_result,
                           english_name=herb.get('english_name', ''), \
                           pinyin_name=herb.get('pinyin_name', ''), \
                           chinese_name=herb.get('chinese_name', ''), \
                           other_name=herb.get('other_name', ''), \
                           intro=herb.get('summary', ''), \
                           conditions=herb.get('new_conditions', ''), \
                           interactions=herb.get('interactions', ''), \
                           safe=herb.get('safe', ''), \
                           likely_safe=herb.get('likely_safe', ''), \
                           possibly_safe=herb.get('possibly_safe', ''), \
                           likely_unsafe=herb.get('likely_unsafe', ''), \
                           possibly_unsafe=herb.get('possibly_unsafe', '')
                          )







@app.route('/lookup', methods=['GET'])
def lookup():
    
    herb_id = request.args.get('herb_id')  
    
    herb = ds.get_herb(int(herb_id))
    
    return render_template('lookup_jinja.html', \
                           english_name=herb.get('english_name', ''), \
                           pinyin_name=herb.get('pinyin_name', ''), \
                           chinese_name=herb.get('chinese_name', ''), \
                           other_name=herb.get('other_name', ''), \
                           intro=herb.get('summary', ''), \
                           conditions=herb.get('new_conditions'), \
                           interactions=herb.get('interactions'), \
                           safe=herb.get('safe'), \
                           likely_safe=herb.get('likely_safe'), \
                           possibly_safe=herb.get('possibly_safe'), \
                           likely_unsafe=herb.get('likely_unsafe'), \
                           possibly_unsafe=herb.get('possibly_unsafe')
                          )
    

@app.errorhandler(404)
def not_found(e):
    return render_template('404_jinja.html')



if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=8080, debug=True)
