#!/usr/bin/env python
import sys
import os
import os.path
import sqlite3
import xmlite
import xmlite.load
from lxml import etree

class Ops(object):
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)

	def db(self):
		return sqlite3.connect(self.db_path)

	def db_exec_file(self, path):
		return self.db().executescript(open(path).read())

	def db_schema(self):
		return open(os.path.join(xmlite.__path__[0], 'schema.ddl.sql')).read()

	def db_remove(self):
		if os.path.exists(self.db_path):
			os.unlink(self.db_path)

	def db_create(self):
		return self.db().executescript(self.db_schema())

	def load_file(self):
		self.doc = xmlite.load.load_file(self.file, self.db(), self.location)

	def file_open(self):
		self.file = open(self.file_path)

	def file_stdin(self):
		self.file = sys.stdin

	def dump_doc(self):
		open(self.file_path, 'w').write(xmlite.load.db_xml_string(self.db(), self.doc))

	def location_by_path(self):
		self.location = os.path.split(self.file_path)[1]

	argtypes = {
		'doc': int
	}

	def arg_type(self, arg_name):
		return self.argtypes.get(arg_name, str)

try:
	from collections import OrderedDict as commands_dict
except ImportError:
	commands_dict = dict

class Shell(Ops):
	commands = commands_dict((
		# command: ([0]="arg1, arg2, ..", [1]="op1, op2, ...", [2]="Help string")
		('create', ("db_path", "db_create", "Creates empty db")),
		('recreate', ("db_path", "db_remove db_create", "Removes and rereates empty db")),
		('recreate_from_file', (
			"file_path db_path", "location_by_path db_remove db_create file_open load_file",
			"Removes, creates empty and loads the file as doc into db"
			)),
		('load', (
			"file_path db_path", "location_by_path file_open load_file",
			"Loads file as doc into existing db with file name as location"
			)),
		('load_stdin', (
			"location db_path", "file_stdin load_file",
			"Loads stdin as doc into existing db as location"
			)),
		('mat_dump', ("db_path doc file_path", "dump_doc", "First materializes a doc into memory and then prints it")),
	))

	def usage_lines(self):
		yield '\nCommands:\n-----------'
		for command, cdef in self.commands.items():
			yield "%s %s\n#%s\n" % (command, cdef[0], cdef[2])
		yield ''


def test01():
	ops = Ops(
		db_path = '/home/alek/tmp/repodata.sqlite',
		file_path = '/home/alek/tmp/primary.xml',
		location = 'primary.xml'
		)
	ops.db_remove()
	ops.db_create()
	ops.load_file()


def main():
	sh = Shell()
	command = sh.commands.get(sys.argv[1])
	if command:
		for i, arg in enumerate(command[0].split(), 2):
			setattr(sh, arg, sh.arg_type(arg)(sys.argv[i]))

		for meth in command[1].split():
			getattr(sh, meth)()
	else:
		sys.stderr.write('\n'.join(sh.usage_lines()))

main()
