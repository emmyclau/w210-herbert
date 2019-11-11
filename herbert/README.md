# Herbert Website Code

This directory contains all the flask code to build the website.

Directory layout

```bash
├── Herbert/ # Contains the whole app
│   ├── data/ 
│   │   └── # Contains SQLAlchemy Models
│   ├── index/
│   │   └── # Contains Whoosh index
│   ├── services/
│   │   └── # Contains python code for app functions
│   ├── static/
│   │   ├── css/
│   │   │   └─ # Stylesheets
│   │   ├── img/
│   │   │   └─ # Images
│   │   └── js/
│   │       └─ # Javascript
│   ├── templates/
│   │   └── # All html Jinja2 templates for views
│   ├── views/
│   │   └── # All flask blueprints
│   └── __init__.py # Contains the function to build the app
```

Run by running 

```bash
$ export FLASK_APP="herbert"
$ flask run
```