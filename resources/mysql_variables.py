from flask_restful import Resource, request
from mysql.connector import MySQLConnection 

class MySQLVariables(Resource):
	def __init__(self, host=None, port=None):
		try:
			self.cnx = MySQLConnection(host=host, port=port)
			self.cursor = self.cnx.get_cursor()
		except:
			raise

	def get(self, host=None, port=None, var=None):
		mysql_variables = { }
		if var is None:
			sql = "show global variables;"
		else:
			sql = "show global variables like '%s';" % var
		self.cursor.execute(sql)
		for row in self.cursor:
			mysql_variables[row['Variable_name']] = row['Value']
		self.cursor.close()
		return mysql_variables

	def put(self, host=None, port=None, var=None):
		if var:
			sql = "set global %s = '%s';" % (var, request.form['value'])
			self.cursor.execute(sql)
			self.cursor.close()
		return {}

			# show global variables like '';
		#show global variables;
