#!/usr/bin/env python


import logging
from StringIO import StringIO
from cgi import escape
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.db import Key
import json
from time import sleep
from array import *
from urllib import urlencode

class StoredData(db.Model):
  tag = db.StringProperty()
  value = db.StringProperty(multiline=True)

  date = db.DateTimeProperty(required=True, auto_now=True)


IntroMessage = '''
<table border=0>
<tr valign="top">
<td><image src="/images/customLogo.gif" width="200" hspace="10"></td>
<td>
<p>
This web service is designed to work with <a
href="http://appinventor.googlelabs.com">App Inventor
for Android</a> and the TinyWebDB component. The end-goal of this service is
to communicate with a mobile app created with App Inventor.
</p>
The page your are looking at is 
a web page interface to the web service to help programmers with debugging. You
can invoke the get and store operations by hand, view the existing entries, and also delete individual entries.</p>

</td> </tr> </table>'''


class MainPage(webapp.RequestHandler):

  def get(self):
    write_page_header(self);
    self.response.out.write(IntroMessage)
    write_available_operations(self)
    show_stored_data(self)
    self.response.out.write('</body></html>')


class StoreAValue(webapp.RequestHandler):

  def store_a_value(self, tag, value):
    # There's a potential readers/writers error here :(
    entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
    if entry:
      entry.value = value
    else: entry = StoredData(tag = tag, value = value)
    entry.put()
    ## Send back a confirmation message. 
    result = ["STORED", tag, value]
    WritePhoneOrWeb(self, lambda : json.dump(result, self.response.out))

  def post(self):
    tag = self.request.get('tag')
    value = self.request.get('value')
    self.store_a_value(tag, value)

  def get(self):
    self.response.out.write('''
    <html><body>
    <form action="/storeavalue" method="post"
          enctype=application/x-www-form-urlencoded>
       <p>Tag<input type="text" name="tag" /></p>
       <p>Value<input type="text" name="value" /></p>
       <input type="hidden" name="fmt" value="html">
       <input type="submit" value="Store a value">
    </form></body></html>\n''')


  def store_a_value(self, tag, value):
    # There's a potential readers/writers error here :(
    entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
    if entry:
      entry.value = value
    else: entry = StoredData(tag = tag, value = value)
    entry.put()
    ## Send back a confirmation message.  
    result = ["STORED", tag, value]
    WritePhoneOrWeb(self, lambda : json.dump(result, self.response.out))

  def post(self):
    tag = self.request.get('tag')
    value = self.request.get('value')
    self.store_a_value(tag, value)

  def get(self):
    self.response.out.write('''
    <html><body>
    <form action="/storeavalue" method="post"
          enctype=application/x-www-form-urlencoded>
       <p>Tag<input type="text" name="tag" /></p>
       <p>Value<input type="text" name="value" /></p>
       <input type="hidden" name="fmt" value="html">
       <input type="submit" value="Store a value">
    </form></body></html>\n''')
	
class GetValue(webapp.RequestHandler):

  def get_value(self, tag):
	if tag == "getList":

		listTags = ['reservationsMaths','reservationsScience','reservationsTechnology','reservationsPhysics','reservationsLibrary','reservationsEngineering','reservationsHumanities','reservationsGeneral','reservationsStudy Area','reservationsSuite']

		valuesAll = ""
		for tags in listTags:
                	entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tags).get()
			if entry:
			  value = str(entry.value)
			else: value = ""
                        valuesAll += value + "x"
                        		
			## We tag the returned result with "VALUE"
                if self.request.get('fmt') == "html":
                  value = escape(valuesAll)
                  tag = escape(tag)
                WritePhoneOrWeb(self, lambda : json.dump(["VALUE", "getList", valuesAll], self.response.out))
                sleep(1)
        elif "delete" in tag :
		    tagToDelete = tag[6:]
		    tagToDelete = "username" + tagToDelete
		    entry = StoredData.all().filter('tag =', tagToDelete)
		    for entries in entry:
                      entry_key_string = str(tagToDelete.key())
		    delete = DeleteEntry()
		    form = {'entry_key_string': entry_key_string,'tag': tagToDelete, 'fmt': 'html'}
		    form = urlencode(form)
		    delete.Response = webapp.Response()
		    delete.request = webapp.Request({
                                          'REQUEST_METHOD': 'POST',
                                          'PATH_INFO': '/deleteentry',
                                          'wsgi.input': StringIO(form),
                                          'CONTENT_LENGTH': len(form),
                                          
                                          'SERVER_PORT': '80',
                                          'wsgi.url_scheme': 'http',
                                      })
		    delete.post()
	else:
		entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
	
		if entry:
		  value = entry.value
		else: value = ""
		## We tag the returned result with "VALUE"
		if self.request.get('fmt') == "html":
		  ##value = escape(value)
		  tag = escape(tag)
		WritePhoneOrWeb(self, lambda : json.dump(["VALUE", tag, value], self.response.out))

  def post(self):
    tag = self.request.get('tag')
    self.get_value(tag)

  def get(self):
    self.response.out.write('''
    <html><body>
    <form action="/getvalue" method="post"
          enctype=application/x-www-form-urlencoded>
       <p>Tag<input type="text" name="tag" /></p>
       <input type="hidden" name="fmt" value="html">
       <input type="submit" value="Get value">
    </form></body></html>\n''')




class DeleteEntry(webapp.RequestHandler):

  def post(self):
    logging.debug('/deleteentry?%s\n|%s|' %
                  (self.request.query_string, self.request.body))
    entry_key_string = self.request.get('entry_key_string')
    key = db.Key(entry_key_string)  
    tag = self.request.get('tag')
    db.run_in_transaction(dbSafeDelete,key)
    self.redirect('/')


def write_available_operations(self):
  self.response.out.write('''
    <p>Available calls:\n
    <ul>
    <li><a href="/storeavalue">/storeavalue</a>: Stores a value, given a tag and a value</li>
    <li><a href="/getvalue">/getvalue</a>: Retrieves the value stored under a given tag.  Returns the empty string if no value is stored</li>
    </ul>''')


def write_page_header(self):
  self.response.headers['Content-Type'] = 'text/html'
  self.response.out.write('''
     <html>
     <head>
     <style type="text/css">
        body {margin-left: 5% ; margin-right: 5%; margin-top: 0.5in;
             font-family: verdana, arial,"trebuchet ms", helvetica, sans-serif;}
        ul {list-style: disc;}
     </style>
     <title>Tiny WebDB</title>
     </head>
     <body>''')
  self.response.out.write('<h2>App Inventor for Android: Custom Tiny WebDB Service</h2>')


def show_stored_data(self):
  self.response.out.write('''
    <p><table border=1>
      <tr>
         <th>Key</th>
         <th>Value</th>
         <th>Created (GMT)</th>
      </tr>''')

  entries = StoredData.all().order("-tag")
  for e in entries:
    entry_key_string = str(e.key())
    self.response.out.write('<tr>')
    self.response.out.write('<td>%s</td>' % escape(e.tag))
    self.response.out.write('<td>%s</td>' % escape(e.value))      
    self.response.out.write('<td><font size="-1">%s</font></td>\n' % e.date.ctime())
    self.response.out.write('''
      <td><form action="/deleteentry" method="post"
            enctype=application/x-www-form-urlencoded>
	    <input type="hidden" name="entry_key_string" value="%s">
	    <input type="hidden" name="tag" value="%s">
            <input type="hidden" name="fmt" value="html">
	    <input type="submit" style="background-color: red" value="Delete"></form></td>\n''' %
                            (entry_key_string, escape(e.tag)))
    self.response.out.write('</tr>')
  self.response.out.write('</table>')





def WritePhoneOrWeb(handler, writer):
  if handler.request.get('fmt') == "html":
    WritePhoneOrWebToWeb(handler, writer)
  else:
    handler.response.headers['Content-Type'] = 'application/jsonrequest'
    writer()

#### Result when writing to the Web
def WritePhoneOrWebToWeb(handler, writer):
  handler.response.headers['Content-Type'] = 'text/html'
  handler.response.out.write('<html><body>')
  handler.response.out.write('''
  <em>The server will send this to the component:</em>
  <p />''')
  writer()
  WriteWebFooter(handler, writer)


def WriteToWeb(handler, writer):
  handler.response.headers['Content-Type'] = 'text/html'
  handler.response.out.write('<html><body>')
  writer()
  WriteWebFooter(handler, writer)

def WriteWebFooter(handler, writer):
  handler.response.out.write('''
  <p><a href="/">
  <i>Return to Game Server Main Page</i>
  </a>''')
  handler.response.out.write('</body></html>')

def dbSafeDelete(key):
  if db.get(key) :  db.delete(key)


application =     \
   webapp.WSGIApplication([('/', MainPage),
                           ('/storeavalue', StoreAValue),
                           ('/deleteentry', DeleteEntry),
                           ('/getvalue', GetValue)
                           ],
                          debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()


