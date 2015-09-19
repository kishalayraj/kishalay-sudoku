import os
import urllib
import Generator
import Solver
import random

from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

sent_cells = ['0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0']

sol_cells = ['0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0',
		      '0','1','0','1','0','1','0','1','0']


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    cells = ndb.StringProperty(repeated=True,indexed=False)
    


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    sudoku_id = ndb.IntegerProperty(indexed=False)

class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(1)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Guestbook(webapp2.RequestHandler):
 
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))
        
        greeting.content = self.request.get('content')
        level = 0
        #greeting.sudoku_id = random.randint(0,99)
        greeting.sudoku_id = 0
        
        if greeting.content == "Easy":
	    level = 1
	if greeting.content == "Medium":
	    level = 2
	if greeting.content == "Difficult":
	    level = 3

        s = [[0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0]]
	
	s1 = [0,0,0,0,0,0,0,0,0,
	     0,0,0,0,0,0,0,0,0,
	     0,0,0,0,0,0,0,0,0,
	     0,0,0,0,0,0,0,0,0,
	     0,0,0,0,0,0,0,0,0,
	     0,0,0,0,0,0,0,0,0,
	     0,0,0,0,0,0,0,0,0,
	     0,0,0,0,0,0,0,0,0,
	     0,0,0,0,0,0,0,0,0]
	
        Generator.fill_sudoku(s,0,0)
        Generator.reduce_sudoku(s,level)
        
        for i in range(0,9):
	    for j in range(0,9):
		sent_cells[9*i+j]=str(s[i][j])
	
	"""fname = 'SudokuPuzzles.txt'
	with open(fname) as f:
	    content = f.readlines()

	content = [x.strip('\n') for x in content] 
	s1 = content[greeting.sudoku_id]
	
	for i in range(0,81):
	    sent_cells[i] = str(s1[i])"""
	    
        if users.get_current_user():
            greeting.author = Author(
                    identity= users.get_current_user().user_id(),
                    email= users.get_current_user().email(),
                    cells= sent_cells)

        
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        
        #taskqueue.add(url='/genSudoku', params={'key': greeting.content})
        
        self.redirect('/?' + urllib.urlencode(query_params))

class CheckSudoku(webapp2.RequestHandler):
    
    def post(self):
	guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(1)
        
	s = [[0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0]]
	
	for i in range(0,81):
	    row = i // 9
	    col = i % 9
	    if sent_cells[i] != '':
		s[row][col] = int(sent_cells[i])
	    else:
		s[row][col] = 0
		
	for greeting in greetings:
	    for i in range(0,81):
		if sent_cells[i] == '0':
		    sent_cells[i] = str(self.request.get('e'+str(i/9)+str(i%9)))
	
	    """fname = 'Solutions.txt'
	    with open(fname) as f:
		content = f.readlines()
	
	    content = [x.strip('\n') for x in content] 
	    s = content[greeting.sudoku_id]"""
	    
	    Solver.initial_fill(s)
	    
	    for line in s:
		if 0 in line:
		    Solver.solve(s, 0, 0)
		    break
	    
	    for i in range(0,9):
		for j in range(0,9):
		    sol_cells[9*i+j] = str(s[i][j])
	    
	    flag = True
	    for i in range(0,81):
		if sol_cells[i] != sent_cells[i]:
		    flag = False
		    break
	
	
	template_values = {
	  'flag': flag,
	  'sol_cells': sol_cells,
	  }
	template = JINJA_ENVIRONMENT.get_template('result.html')
        self.response.write(template.render(template_values))
        
"""class GenSudoku(webapp2.RequestHandler):
    def post(self):
	key = self.request.get('key')
	@ndb.transactional
	def gen():
	    s = [[0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0]]
	    
	    Generator.populate_board(s,0,0)
	    Generator.reduce_sudoku(s,1)
	    fname = 'SudokuPuzzles.txt'
	    f = open(fname, "w")
	    output = ""
	    for i in range(9):
		for j in range(9):
		    output += str(s[i][j])
	    output = output + "\n"
	    f.write(output)
	
	gen()"""

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/checkSudoku', CheckSudoku),
], debug=True)
