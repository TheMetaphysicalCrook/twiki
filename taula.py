#!/usr/bin/env python

from flask import Flask, g, jsonify, request, make_response, render_template, url_for, flash, redirect, abort, send_from_directory, Markup

import os, os.path, csv, glob, copy, shutil, re

from time import gmtime, strftime


from datetime import date
import jsonpickle


# Variables globals

datafile = "./data.json" # On des totes les coses
encrypted = False # Si he d'encriptar o no el wiki

# Initialize app and setting secret key for flash messages 
app = Flask(__name__)
app.secret_key = 'el meu secret'

# Classes
class Tiddler(object):
	"""Class Tiddler. Emulates the Tiddlywiki's tiddler.
		- title: the title of the Tiddler. Mandatory. Unique field.
		- created: the date of creation (ISO 8601 format, 'YYYY-MM-DD')
		- modified: the date of modification (ISO 8601 format, 'YYYY-MM-DD')
		- tags: a list of `str`.
		- attached: a list of `str`. Attached files for adding their content for searching text
		- fieldset: a list of tuples (field, value). Each value is supposed to be a `str`.
		  Eg. `('author', 'me')`, `('lang', 'ca')`, `('license', 'CC-BY 4.0')`, etc.
		  You can add user-defined fields adding to `fieldset` list
	"""

	title = None
	created = None
	modified = None
	tags = []
	attached = []
	fieldset = []
	

	def __init__(self, title):
		self.title = title
		self.created = date.today().isoformat()
		self.modified = date.today().isoformat()

	def __repr__(self):
		return '<Tiddler %r>' % self.title

# Methods

## Auxiliar functions
def tiddler_select(title):
	"""Selects the tiddler with self.title=title"""

	with open(datafile, 'r') as f:
		tiddlers = jsonpickle.decode(f.read())
		existing = [t for t in tiddlers if t.title == title]
		if len(existing) == 0:
			return None
		else:
			return existing[0]

def tiddlers_list():
	"""Returns all tiddlers as a list"""

	with open(datafile, 'r') as f:
		return jsonpickle.decode(f.read())	

## Web application functions
### List
@app.route("/tiddler/list", methods=['GET'])
def tiddler_list():
	"""Lists tiddlers with their information"""
	
	tiddlers = tiddlers_list()
	return render_template('tiddler_list.html', tiddlers=tiddlers)

### Detail
@app.route("/tiddler/<title>", methods=['GET'])
def tiddler_show(title):
	"""Shows tiddler with specific title"""

	tiddler = tiddler_select(title)
	
	if tiddler == None:
		abort(404)
	else:
		return render_template('tiddler_show.html', tiddler=tiddler)

## Edit tiddler
@app.route('/tiddler/edit/<title>', methods = ['GET'])
def tiddler_edit(title):
	"""Edits tiddler"""

	tiddler = tiddler_select(title)
	
	if tiddler == None:
		abort(404)
	else:
		return render_template('tiddler_edit.html', tiddler=tiddler)


## Modify tiddler
@app.route('/tiddler/update/<title>', methods = ['POST'])
def tiddler_update(title):
	"""Update tiddler"""

	tiddlers = tiddlers_list()
	tiddler = tiddler_select(title)
	
	if tiddler == None:
		abort(404)
	else:
		# The tiddler actually exists
		form_title = request.form.get('title')
		if form_title != tiddler.title:
			existing_tiddler = tiddler_select(form_title)
			if existing_tiddler != None:
				abort(409, "Previous existing tiddler with the same title")
			else:
				tiddler.title = form_title
				tiddler.tags = request.form.get('tags')
				tiddler.created = request.form.get('created')
				tiddler.modified = date.today().isoformat()
				tiddler.attached = request.form.get('attached')
				#tiddler.fieldset = TODO
		else:
			tiddler.title = form_title
			tiddler.tags = request.form.get('tags')
			tiddler.created = request.form.get('created')
			tiddler.modified = date.today().isoformat()
			tiddler.attached = request.form.get('attached')
			#tiddler.fieldset = TODO

		#gravar al fitxer: # https://stackoverflow.com/questions/2582138/finding-and-replacing-elements-in-a-list-python
		tiddlers = [tiddler if t.title==title else t for t in tiddlers]
		
		with open(datafile, 'w') as f:
			f.write(jsonpickle.encode(tiddlers))

	return render_template('tiddler_list.html', tiddlers=tiddlers)


## Index
@app.route("/", methods=['GET'])
def index():		
	return redirect(url_for('tiddler_list'))

## Errors
@app.errorhandler(404)
def error_no_trobat(error):
	return render_template('error.html', error=error), 404

@app.errorhandler(406)
def error_conflicte(error):
	return render_template('error.html', error=error), 406

@app.errorhandler(500)
def error_intern(error):
	return render_template('error.html', error=error), 500


# Main procedure
if __name__ == "__main__":
	app.run(debug=True, port=8080)
