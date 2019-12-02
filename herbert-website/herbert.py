from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from data_source import DataSource_Herb, DataSource_Condition, DataSource_Interaction
from search import SearchEngine_Herb, SearchEngine_Condition, SearchEngine_Interaction, Herbert_SpellChecker
import urllib.parse


# start flask webserver
app = Flask(__name__)
bootstrap = Bootstrap(app)


# data source and search engine for herbs
ds_herb = DataSource_Herb()
se_herb = SearchEngine_Herb(ds_herb)

# data source and search engine for conditions
ds_condition = DataSource_Condition()
se_condition = SearchEngine_Condition(ds_condition)

# data source and search engine for interactions
ds_interaction = DataSource_Interaction()
se_interaction = SearchEngine_Interaction(ds_interaction)

# spell checker
spellchecker = Herbert_SpellChecker(ds_herb)


# index.html
@app.route('/', methods=['GET'])
def index():
    return render_template('index_jinja.html')

# search all 
@app.route('/search', methods=['GET'])
def search():
    
    # get query
    query = request.args.get('query')  
   
    if (query is None):
        query = ''   
    
    query = urllib.parse.unquote(query)

    # search result 
    search_result = se_herb.search(query)

    # no result
    if len(search_result) == 0:
        new_query = spellchecker.check(query)
        return render_template('404_jinja.html', query=query, new_query=new_query)
        
    herb = search_result[0]
    
    return render_template('result_jinja.html', \
                           query=query, \
                           search_result = search_result,\
                           english_name=herb.get('english_name', ''), \
                           pinyin_name=herb.get('pinyin_name', ''), \
                           chinese_name=herb.get('chinese_name', ''), \
                           other_name=herb.get('other_name', ''), \
                           intro=herb.get('summary', ''), \
                           intro_url=herb.get('summary_url', ''), \
                           conditions=herb.get('valid_conditions', ''), \
                           interactions=herb.get('interactions', ''), \
                           safe=herb.get('safe', ''), \
                           likely_safe=herb.get('likely_safe', ''), \
                           possibly_safe=herb.get('possibly_safe', ''), \
                           likely_unsafe=herb.get('likely_unsafe', ''), \
                           possibly_unsafe=herb.get('possibly_unsafe', '')
                          )

# search condition
@app.route('/search_condition', methods=['GET'])
def search_condition():
    
    # get query
    query = request.args.get('query')  
    
    if query is None:
        query = ''   
    
    query = urllib.parse.unquote(query)
    
    # search result 
    search_result = se_condition.search(query)
    
    # no result
    if len(search_result) == 0:
        new_query = spellchecker.check(query)
        return render_template('404_condition_jinja.html', query=query, new_query=new_query)
    
    condition = search_result[0]
    
    return render_template('condition_result_jinja.html', \
                           query=query, \
                           search_result = search_result,\
                           condition_id=condition.get('condition_id', ''), \
                           condition=condition.get('condition', ''), \
                           intro=condition.get('summary', ''),\
                           intro_url=condition.get('summary_url', ''), \
                           herbs=condition.get('all_herbs', '')
                          )
# search interaction
@app.route('/search_interaction', methods=['GET'])
def search_interaction():
    
    # get query
    query = request.args.get('query')  
    
    if query is None:
        query = ''   
    
    query = urllib.parse.unquote(query)
    
    # search result 
    search_result = se_interaction.search(query)
    
    # no result
    if len(search_result) == 0:
        new_query = spellchecker.check(query)
        return render_template('404_interaction_jinja.html', query=query, new_query=new_query)

    
    interaction = search_result[0]
     
    return render_template('interaction_result_jinja.html', \
                           query=query, \
                           search_result = search_result,
                           interaction_id=interaction.get('interaction_id', ''), \
                           interaction=interaction.get('interaction', ''), \
                           intro=interaction.get('summary', ''),\
                           intro_url=interaction.get('summary_url', ''), \
                           herbs=interaction.get('all_herbs', '')
                          )

# display herb 
@app.route('/herb', methods=['GET'])
def herb():
    
    herb_id = request.args.get('herb_id')  
    
    if herb_id is None:
        return ''
    
    herb = ds_herb.get_herb(int(herb_id))
    
    return render_template('lookup_jinja.html', \
                           english_name=herb.get('english_name', ''), \
                           pinyin_name=herb.get('pinyin_name', ''), \
                           chinese_name=herb.get('chinese_name', ''), \
                           other_name=herb.get('other_name', ''), \
                           intro=herb.get('summary', ''), \
                           intro_url=herb.get('summary_url', ''), \
                           conditions=herb.get('valid_conditions', ''), \
                           interactions=herb.get('interactions', ''), \
                           safe=herb.get('safe', ''), \
                           likely_safe=herb.get('likely_safe', ''), \
                           possibly_safe=herb.get('possibly_safe', ''), \
                           likely_unsafe=herb.get('likely_unsafe', ''), \
                           possibly_unsafe=herb.get('possibly_unsafe', '')
                          )

# display condition 
@app.route('/condition', methods=['GET'])
def condition():
    
    condition_id = request.args.get('condition_id')  
    
    if condition_id is None:
        return ''
    
    condition = ds_condition.get_condition(int(condition_id))
    
    
    return render_template('lookup_condition_jinja.html', \
                           condition_id=condition.get('condition_id', ''), \
                           condition=condition.get('condition', ''), \
                           intro=condition.get('summary', ''),\
                           intro_url=condition.get('summary_url', ''), \
                           herbs=condition.get('all_herbs', '')
                          )

# display interaction 
@app.route('/interaction', methods=['GET'])
def interaction():
    
    interaction_id = request.args.get('interaction_id')  
    
    if interaction_id is None:
        return ''
    
    interaction = ds_interaction.get_interaction(int(interaction_id))
    
    
    return render_template('lookup_interaction_jinja.html', \
                           interaction_id=interaction.get('interaction_id', ''), \
                           interaction=interaction.get('interaction', ''), \
                           intro=interaction.get('summary', ''),\
                           intro_url=interaction.get('summary_url', ''), \
                           herbs=interaction.get('all_herbs', '')
                          )
      
# display all herbs 
@app.route('/all', methods=['GET'])
def all():
    return render_template('all_herb_jinja.html',
                           herbs=ds_herb.get_all())
      
 
    
    
    
# error page
@app.errorhandler(404)
def not_found(e):
    return render_template('404_jinja.html')



if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=8080, debug=True)
