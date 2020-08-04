
# GGCode Python Flask API Project Template

## Installation

Pre requisite:
- Python 3.7
- Python Virtual Environment (we usually use this https://pypi.org/project/virtualenv/)
- MariaDB database
- MongoDB
- Redis

Install Command:
- Create MariaDB database, clone & follow the instruction from https://github.com/abcdef-id/python-mysql-migration.git
- Activate your Python Virtual Environment, if using virtualenv: 
```
<virtualenv_directory>/bin/activate
```
- Install Libraries:
```
pip install -r requirement.txt
```
- create folder logs, run this command from project root:
```
mkdir -p app/resources/logs
```

Uninstall Command:
- Remove libraries: 
```
pip uninstall -r requirement.txt
```


## Run
- copy file config.cfg.example to config.cfg
- change project mysql connection in config.cfg
- run:
```
python run.py
```

Import file **python-api.postman_collection** to your postman to try the restful api and try it.

Login:
- api url: POST http://127.0.0.1:8899/api/v1/user/login
- header: Content-Type:application/json
- request parameter: { "username":"admin", "password":"123456" }

User List:
- api url: POST http://127.0.0.1:8899/api/v1/user/list
- header: 
Authorization:Bearer <jwt_token>
Content-Type:application/json
- request parameter: 
{ 
	"rp":<RecordPerPage>, 
	"p":<Page>, 
	"f":{"<field_name>":"<field_value"},
	"o":{"<field_name>":"<asc_desc>"},
}

## Directory Structure

- app/apis/ : code location for api controller
- app/libraries/ : code location for global function
- app/models/ : code location for data model
- app/static/ : location for static file

## Template Files
- app/__init__.py : code to initiate app configuration 
- app/config.py : code to read config.cfg files
- app/routes.py : code to load api controller files & routes
- app/variable_constant.py : code for global constant & variable
- app/apis/base_api.py : code for api superclass, contains default api function
- app/models/base_model.py : code for model superclass, contains default models function


## How to write

This project template use [Flask Restful](https://flask-restful.readthedocs.io/en/latest/) and [Blueprint](https://flask.palletsprojects.com/en/1.1.x/tutorial/views/)

### Create your Model

#### Create file model in [**app/models/**](https://github.com/abcdef-id/python-api/tree/master/app/models) directory. See the model example in [**app/models/user.py**](https://github.com/abcdef-id/python-api/blob/master/app/models/user.py)

```
from app.models.base_model import CrudBase

class <model_class_name>(CrudBase):

    __table__ = '<table_name>' # What is the table for this Model
    
    __primary_key__ = 'id' # What is the primary key for this table

    # Define which columns can be added.
    __add_new_fillable__ = [
        '<field_name_1>',
        '<field_name_2>',
        '<field_name_3>',
        'status',
        'created_by'
    ]

    #Define which columns can be updated.
    __update_fillable__ = [
	'<field_name_1>',
        '<field_name_2>',
        '<field_name_3>',
        'status',
	'updated_by'
    ]

    # Define form input validation, Use this in api validation.
    addNewValidation = {
	'<field_name_1>': {'type': 'string', 'required': True, 'empty': False},
	'<field_name_2>': {'type': 'string', 'required': True, 'empty': False},
	'<field_name_3>': {'type': 'string', 'required': True, 'empty': False},
    }

    updateValidation = {
	'<field_name_1>': {'type': 'string', 'required': True, 'empty': False},
	'<field_name_2>': {'type': 'string', 'required': True, 'empty': False},
	'<field_name_3>': {'type': 'string', 'required': True, 'empty': False},
    }
```

We provide **CrudBase** Class for **MySQL** and **CrudBaseMongoDB** Class for MongoDB if it is standard List and CRUD. 

CrudBase Contain methods:

**# getList**, with parameters:
- **args** with value below:
```
{ 
	"rp":<RecordPerPage>, 
	"p":<Page>, 
	"f":{"<query_field_name>":"<field_value"},
	"o":{"<order_field_name>":"<asc_desc>"}
}
```
- **qraw** (optional) if you want to use raw query value, example: ' id=1 and status=1 '

usage in api:
```
    args = { 
	"rp":25, 
	"p":1, 
	"f":{
	    "field_1":"a",
	    "field_2":"b"
	},
	"o":{
	    "field_1":"asc",
	    "field_2":"desc"
	}
    }
    # Without raw query
    data_list = YourModel.getList(args)
    
    # With raw query
    qraw = ' field_3 like '%abcd% ' 
    data_list = YourModel.getList(args,qraw)
    
```
**# getById**, with parameter:
- **id** <primary_key_value>

usage in api:
```
    id = 1
    single_data = YourModel.getById(id)
```
**# addNew**
- **args** dictionary data
	
usage in api:
```
    args = {
        'field_1':'a',
        'field_2':'b',
        'field_3':'c'
    }
    YourModel.addNew(args)
```

**# doUpdate**
- **id** <primary_key_value>
- **args** dictionary data
usage in api:
```
    id = 1
    args = {
        'field_1':'a',
        'field_2':'b',
        'field_3':'c'
    }
    YourModel.doUpdate(id, args)
```

**# doDelete**
- **id** <primary_key_value>

usage in api:
```
    id = 1
    YourModel.doDelete(id)
```
**# getAll**
usage in api:
```
    data_list = YourModel.getAll()
```
**Make your own method**
in your model class:
```
    from app import db
     
    @classmethod
    def <your_method_name>(self, <your_argument>):
        result = db.<your_query_builder>
        # Your Logic
        return result
```
usage in api:
```
    result = YourModel.<your_method_name>(<your_argument>)
```

Learn orator-orm query builder [here](https://orator-orm.com/docs/0.9/query_builder.html#introduction)

### Create your API

#### 1. Create file api controller in [**app/apis/**](https://github.com/abcdef-id/python-api/tree/master/app/apis) directory. See the controller example in [**app/apis/user.py**](https://github.com/abcdef-id/python-api/blob/master/app/apis/user.py)

Define your blueprint:
```
from flask import Blueprint, request, json
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, \
    jwt_required, create_access_token, create_refresh_token, \
    get_jwt_claims, get_jwt_identity, get_raw_jwt, \
    jwt_refresh_token_required, get_jti
from app import jwt, app, cache, db, revoked_store
from app.apis.base_api import BaseApi, BaseList, BaseCrud
from app.variable_constant import VariableConstant
from app.libraries.validator import MyValidator
from app.libraries.util import Util as util, permission_checker

from app.models.<your_data_model> import <your_data_model_class> as <your_data_model_alias>
from ... import ...
import ...

<your_blueprint> = Blueprint('<your_blueprint_name>', __name__)
api = Api(<your_blueprint>)
```
We provide **BaseList** and **BaseCRUD** Class if it is standard List and CRUD and **BaseAPI** Class if you need to write your own logic. See [**app/apis/base_api.py**](https://github.com/abcdef-id/python-api/blob/master/app/apis/base_api.py). How to use it in your controller:

BaseList:
```
class <your_list_class>(BaseList, Resource):
    def __init__(self):
        super(<your_list_class>, self).__init__(<your_data_model_alias>)

api.add_resource(<your_list_class>, '/list')
```
BaseCRUD:
```
class <your_create_class>(BaseCrud, Resource):
    def __init__(self):
        super(<your_create_class>,self).__init__(<your_data_model_alias>)

class <your_read_update_delete_class>(BaseCrud, Resource):
    def __init__(self):
        super(<your_read_update_delete_class>, self).__init__(<your_data_model_alias>)

api.add_resource(<your_create_class>, '/')
api.add_resource(<your_read_update_delete_class>, '/<string:id>')
```
BaseAPI:
```
class <your_create_class>(BaseApi, Resource):
    def __init__(self):
        super(<your_create_class>, self).__init__()

    def post(self):
        <write_your_code_here>
        
        return  self.response({
		'title': '<response_title>',
		'data': <json_data>,
		'status_code': <http_code>
	})

class <your_read_update_delete_class>(BaseApi, Resource):
    def __init__(self):
        super(<your_read_update_delete_class>, self).__init__()
    
    def get(self,<your_parameter>):
        <write_your_code_here>
        
        return  self.response({
		'title': '<response_title>',
		'data': <json_data>,
		'status_code': <http_code>
	})
	
    def put(self,<your_parameter>):
        <write_your_code_here>
        
        return  self.response({
		'title': '<response_title>',
		'data': <json_data>,
		'status_code': <http_code>
	})

    def delete(self,<your_parameter>):
        <write_your_code_here>
        
        return  self.response({
		'title': '<response_title>',
		'data': <json_data>,
		'status_code': <http_code>
	})

api.add_resource(<your_create_class>, '/')
api.add_resource(<your_read_update_delete_class>, '/<string:<your_parameter>>')
```

use **self.response_plain(<text_data>)** to return text only

#### 2. Add your blueprint in [**app/routes.py**](https://github.com/abcdef-id/python-api/blob/master/app/routes.py)
```
from app.apis.<your_controller> import <your_blueprint>
app.register_blueprint(<your_blueprint>, url_prefix='/api/v1/<your_url_prefix>')
```

