#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
## RANDOM STUPID STUFF I HAVE TO DO CAUSE APP ENGINE SUCKS
try:
    # This is needed to make local development work with SSL.
    # This must be done *before* you import the Braintree Python library.
    # See http://stackoverflow.com/a/24066819/500584
    # and https://code.google.com/p/googleappengine/issues/detail?id=9246 for more information.
    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ssl', '_socket']

    import sys
    # this is socket.py copied from a standard python install
    import stdlib_socket
    sys.modules['socket'] = stdlib_socket
except ImportError as e:
    print(e)



## libraries provided with appengine

import webapp2
from google.appengine.ext import db
import jinja2
import os
from account import User
from RentalAgreement import RentalAgreement
from sign_in_validation import * 
from google.appengine.ext import vendor

## third party libraries
vendor.add('lib')
import braintree
#from requests_toolbelt.adapters import appengine
#appengine.monkeypatch()


## configurations
braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id="2rw4hs8dj6gtgsyx",
                                  public_key="4zg9c6fyy7zwfynh",
                                  private_key="aca22ced99f16bffeac616ffa9e9f3f4")

template_dir = os.path.join( os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)


class MainPage(webapp2.RequestHandler):
    def get(self):
    	form = jinja_env.get_template("form.html")
        self.response.write(
            form.render())

class SignIn(webapp2.RequestHandler):
	def post(self):

		# get post variables
		username = self.request.get('username')
		password = self.request.get('password')
		email = self.request.get('email')
		action = self.request.get('action')

		# validate email
		if action == "Sign Up":
			if sign_in_val(username,password,email):
				user = User(username=username,password=password,email=email)
				user.put()
				self.response.set_cookie('user',username,path='/')
				self.response.headers['Content-Type'] = 'text/html'
				form = jinja_env.get_template("tenant_or_landlord.html")
				self.response.write(form.render())
			else:
				self.response.write("Please try again")
		else:
			user = get_user(username)
			if user and (user.password == password):
				self.response.set_cookie(username,path='/')
				self.response.write(user.username)
			else:
				self.response.write('hmm looks like you\'re not a user')

# after making an account the user goes here and fills out a form

# make ra global for now. definitely bad design. will redo
ra = None

class rentalAgreement(webapp2.RequestHandler):
	def get(self):

		# get variables
		tenants = self.request.get('tenants')
		address = self.request.get('address')
		landlord = self.request.cookies.get('user')

		#make rental agreement datastore 
		global ra
		ra = RentalAgreement(tenants = tenants, address = address, 
			                 emails = " ",phone_number=" ",
			                 names=" ", landlord = landlord)
		ra.put()

		no_tenants = int(tenants)
		## now make other form getting more info
		form = jinja_env.get_template("renter_info.html")
		self.response.write(form.render(n=no_tenants))
	
	## probably bad design to then do post request but works for now
	def post(self):
		names = str(self.request.POST.getall('name'))
		phonenumbers = str(self.request.POST.getall('phonenumber'))
		emails = str(self.request.POST.getall('email'))

		# get the landlord ish out
		#q = db.Query(RentalAgreement)
		#print self.request.cookies.get('user')
		#q.filter('landlord=',self.request.cookies.get('user'))
		#ra = q.get()

		global ra
		# update the row
		ra.emails = emails
		ra.names = names
		ra.phone_number = phonenumbers
		ra.put()
		form = jinja_env.get_template("home.html")
		self.response.write(form.render())


class logout(webapp2.RequestHandler):
	def get(self):
		self.response.delete_cookie('user')
		self.redirect('/')

class payment(webapp2.RequestHandler):
	def get(self):
		token = braintree.ClientToken.generate()
		form = jinja_env.get_template("pay-form.html")
		self.response.write(form.render(token=token))


class Test(webapp2.RequestHandler):
	def get(self):
		t = self.request.GET.getall('q')
		print t

		#q = db.Query(User,keys_only=True)
		#for i in q:
		#	print i.username
		#q.filter('username =','Kamal')
		#x= q.get()
		#print x.username
		#self.response.write(x)



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signin',SignIn),
    ('/test',Test),
    ('/rentalAgreement',rentalAgreement),
    ('/logout',logout),
    ('/payment',payment)
], debug=True)
