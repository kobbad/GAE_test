from account import User
from google.appengine.ext import db


# checks if fields are filled out correctly
# checks if user does not already exist
def sign_in_val(username,password,email):
	## check if the username already exists
	q = db.Query(User)
	q.filter('username =',username)
	user = q.get()

	#check if fields are appropriate
	if (username== "" or password=="") or (email==""):
		return False
	elif '@' not in email or len(email)<=1:
		return False
	elif user:
		return False
	else:
		return True



## this function is to get the user object from the datastore
def get_user(username):
	q = db.Query(User)
	q.filter('username =',username)
	return q.get()