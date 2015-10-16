from flask import Flask, request
from flask_restful import Resource, Api
from resources.mysql_variables import MySQLVariables
from resources.mysql_users import MySQLUsers, MySQLUsersCreate, MySQLUsersAddIp, MySQLUsersDelete
from resources.mysql_resources.users_list import MySQLUsersList

app = Flask(__name__)
api = Api(app)

#api.add_resource(MySQLVariables, '/mysql/servers/<string:host>/<int:port>/variables', '/mysql/servers/<string:host>/<int:port>/variables/<string:var>')
#api.add_resource(MySQLUsers, '/mysql/servers/<string:host>/<int:port>/users', '/mysql/servers/<string:host>/<int:port>/users/<string:user_name>', '/mysql/servers/<string:host>/<int:port>/users/<string:user_name>/<string:user_host>')
#api.add_resource(MySQLUsersList, '/mysql/servers/<string:server_host>/<int:server_port>/users')
api.add_resource(MySQLUsers, '/mysql/users')
#api.add_resource(MySQLUsersCreate, '/mysql/users/create')
api.add_resource(MySQLUsersAddIp, '/mysql/users/add')
api.add_resource(MySQLUsersDelete, '/mysql/users/delete')
if __name__ == '__main__':
    app.run(debug=True)