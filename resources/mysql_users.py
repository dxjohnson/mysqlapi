from flask_restful import Resource
import mysql.connector
import config
import string
from flask_restful import reqparse

#Get: Show all users@host
#Get#User: Show all us
# set port default to 3306? or allow it to be set in config?

class MySQLUsers(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('server', type=unicode, help='Server', required=True)
		parser.add_argument('port', type=int, help='Port', required=True)
		parser.add_argument('users', type=unicode, default=None, help='List of users to view')
		parser.add_argument('hosts', type=unicode, default=None, help='List of hosts for users')

		args = parser.parse_args()
		try:
			server_host = args['server']
			server_port = args['port']
		except:
			# host, port not given
			raise

		users = args['users']
		hosts = args['hosts']

		# Create the SELECT statement
		sql = "SELECT user, host, password FROM mysql.user"
		if users != None or hosts != None:
			sql += " WHERE"

		# Users parameter accepts more then one, so we need to 
		if users != None:
			sql += " user"
			user_array = users.split(',')

			if len(user_array) == 1:
				if users == '\'\'':
					users = "''"
				else:
					users = "'%s'" % users
				sql += " = %s" % users 
			else:
				sql += " IN ("
				count = 0
				for user in user_array:
					if user == '\'\'':
						user = ''
					sql += "'%s'" % user
					count += 1
					if count != len(user_array):
						sql += ","
				sql += ")"

		if users != None and hosts != None:
			sql += " AND"

		if hosts != None:
			sql += " host IN ("
			host_array = hosts.split(',')
			count = 0
			for host in host_array:
				sql += "'%s'" % host
				count += 1
				if count != len(host_array):
					sql += ","
			sql += ")"
		sql += ";"

		print sql
		mysql_users = []
		try:
			cnx = mysql.connector.MySQLConnection(user=config.MYSQL_USER, password=config.MYSQL_PASSWORD, host=server_host, port=server_port)
			cursor = cnx.cursor(dictionary=True)
			cursor.execute(sql)

			for row in cursor:
				user_dict = dict()
				user_dict['user'] = row['user'].decode('utf-8')
				user_dict['host'] = row['host'].decode('utf-8')
				user_dict['password'] = row['password'].decode('utf-8')
				mysql_users.append(user_dict)
			cursor.close()

			for user in mysql_users:
				cursor = cnx.cursor(dictionary=True)
				user_name = user['user']
				user_host = user['host']
				sql = "SHOW GRANTS FOR '%s'@'%s';" % (user_name, user_host)
				cursor.execute(sql)
				grants = list()
				for row in cursor:
					for key, grant in row.iteritems():
						grants.append(grant+";")
				user['grants'] = grants

				cursor.close()
		except mysql.connector.Error as err:
			if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
				print "access denied"
		except:
			raise
		return mysql_users, 200

	def post(self):
		# Look at potential defaults and have some configuration for if they are not provided
		# Example, a password is not required, but a configuration value should be there to require it
		# Need to add the create user options: https://dev.mysql.com/doc/refman/5.5/en/create-user.html
		parser = reqparse.RequestParser()
		parser.add_argument('server', type=unicode, help='Server', required=True)
		parser.add_argument('port', type=int, help='Port', required=True)
		parser.add_argument('user', type=unicode, help='User Name', required=True)
		parser.add_argument('host', type=unicode, help='Source Server', required=True)
		parser.add_argument('password', type=unicode, help='User Password', required=True)
		parser.add_argument('grants', type=unicode, help='User Grants', action='append')

		args = parser.parse_args()
		try:
			server_host = args['server']
			server_port = args['port']
			user = args['user']
			host = args['host']
			password = args['password']
			grants = args['grants']
		except:
			raise

		try:
			cnx = mysql.connector.MySQLConnection(user=config.MYSQL_USER, password=config.MYSQL_PASSWORD, host=server_host, port=server_port)
			cursor = cnx.cursor()
		except:
			raise

		sql = "CREATE USER '%s'@'%s'" % (user, host)
		if len(password) == 41:
			sql += " identified by password '%s';" % (password)
		elif len(password) > 1:
			# figure out the hashing so not to send password unhashed
			sql += " identified by '%s';" % (password)
		else:
			sql += ";"

		try:
			cursor.execute(sql)
		except:
			raise

		try:
			if len(grants) > 0:
				for grant in grants:
					sql = grant + " TO '%s'@'%s';" % (user, host)
					cursor.execute(sql)
		except:
			sql = "DROP USER '%s'@'%s';" % (user, host)
			cursor.execute(sql)
			raise
		else:
			cursor.close()
		return 200

	def put(self):
		

	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('server', type=unicode, help='Server', required=True)
		parser.add_argument('port', type=int, help='Port', required=True)
		parser.add_argument('user', type=unicode, help='User to delete', required=True)
		parser.add_argument('host', type=unicode, help='Host of user to delete', required=True)

		args = parser.parse_args()
		try:
			server_host = args['server']
			server_port = args['port']
			user = args['user']
			host = args['host']
		except:
			raise

		sql = "DROP USER '%s'@'%s'" % (user, host)
		try:
			cnx = mysql.connector.MySQLConnection(user=config.MYSQL_USER, password=config.MYSQL_PASSWORD, host=server_host, port=server_port)
			cursor = cnx.cursor()
			cursor.execute(sql)
			cursor.close()
		except:
			raise

class MySQLUsersCreate(Resource):
	pass

class MySQLUsersDelete(Resource):
	pass

class MySQLUsersClone(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('server', type=unicode, help='Server', required=True)
		parser.add_argument('port', type=int, help='Port', required=True)
		parser.add_argument('user', type=unicode, help='User to copy', required=True)
		parser.add_argument('host', type=unicode, help='Host of user to copy', required=True)
		parser.add_argument('ipaddresses', type=unicode, help='user_name for new user', required=True)
	
		args = parser.parse_args()
		try:
			server_host = args['server']
			server_port = args['port']
			user = args['user']
			host = args['host']
			ip_addresses = args['ipaddresses']
		except:
			raise

		sql = "SHOW GRANTS FOR '%s'@'%s';" % (user, host)

		try:
			cnx = mysql.connector.MySQLConnection(user=config.MYSQL_USER, password=config.MYSQL_PASSWORD, host=server_host, port=server_port)
			cursor = cnx.cursor()
			cursor.execute(sql)

			grants = []
			for grant in cursor:
				grants.append(grant)

			cursor.close()

			cursor = cnx.cursor()
			for ip_address in ip_addresses.split(','):
				for grant in grants:
					# May need to think about using regex searching for @'HERE' to replcae
					sql = string.replace(grant[0], host, ip_address)
					cursor.execute(sql)

			cursor.close()

			# Should return a 201 created
		except:
			raise