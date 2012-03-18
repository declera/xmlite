class XmliteDocMethods(object):
	ctype_cache_class = dict

	__slots__ = (
		'db', 'doc', 'level', 'ix',
		'ctype_get', 'ctype_add', 'ctype_cache',
		'cnode_add', 'cns_add', 'cvalue_add',
	)

	def __init__(self, db, location = None):
		self.db = db
		self.level = 0
		self.ix = 0
		self.ensure_predefined_types()
		self.doc = self.doc_add(location)

		self.ctype_get = db.cursor()
		self.ctype_add = db.cursor()
		self.ctype_cache = self.ctype_cache_class()
		self.cnode_add = db.cursor()
		self.cns_add = db.cursor()
		self.cvalue_add = db.cursor()
		self.init()

	def init(self):
		pass

	def doc_add(self, location):
		c = self.db.cursor()
		c.execute("insert into doc(location) values(?)", (location,))
		return c.lastrowid

	def doc_type_sget(self, qname):
		if qname in self.ctype_cache:
			return self.ctype_cache[qname]

		args = (qname,)
		self.ctype_get.execute("select doc_type from doc_type where qname = ? limit 1", args)
		rows = self.ctype_get.fetchall()
		if rows:
			doc_type = row[0][0]
		else:
			self.ctype_add.execute("insert into doc_type(qname) values(?)", args)
			doc_type = self.ctype_add.lastrowid

		self.ctype_cache[qname] = doc_type
		return doc_type

	def doc_node_add(self, qname):
		self.cnode_add.execute(
			"insert into doc_node(doc, doc_ix, doc_level, doc_type) values(?, ?, ?, ?)",
			(self.doc, self.ix, self.level, qname if type(qname) is int else self.doc_type_sget(qname))
		)
		return self.cnode_add.lastrowid

	def doc_ns_add(self, doc_node, prefix, uri):
		self.cns_add.execute(
			"insert into doc_ns(doc_node, prefix, uri) values(?, ?, ?)",
			(doc_node, prefix, uri)
		)
		return self.cns_add.lastrowid

	def doc_value_add(self, doc_node, qname, value):
		self.cvalue_add.execute(
			"insert into doc_value(doc_node, doc_type, value) values(?, ?, ?)",
			(doc_node, qname if type(qname) is int else self.doc_type_sget(qname), value)
		)
		return self.cvalue_add.lastrowid

	def doc_finalize(self):
		self.db.commit()

	ref_pytype = type(3)
	predefined_types = [
		(3, 'text()'),
		(4, 'text-cdata()'),
		(7, 'processing-instruction()'),
		(8, 'comment()'),
	]

	def ensure_predefined_types(self):
		c = self.db.cursor()
		for doc_type in self.predefined_types:
			c.execute("insert into doc_type(doc_type, qname) values(?, ?)", doc_type)
		c.close()

class XmliteDocBuilder(XmliteDocMethods):
	'''etree handler callbacks'''

	__slots__ = (
		'text' # accumulator keeping last text node, unless considered ignorable
	)

	def init(self):
		self.text = None

	def data2(self, data = None):
		if not len(self.text.lstrip()) == 0:
			self.doc_value_add(self.doc_node_add(3), 3, self.text)
		self.text = data

	def start(self, qname, attrs, nsmap):
		if not self.text is None:
			self.data2()

		self.ix += 1
		doc_node = self.doc_node_add(qname)
		if nsmap:
			for k,v in nsmap.items():
				self.doc_ns_add(doc_node, k, v)
		if attrs:
			for k,v in attrs.items():
				self.doc_value_add(doc_node, k, v)
		self.level += 1

	def end(self, tag):
		if not self.text is None:
			self.data2()

		self.level -= 1

	def data(self, data):
		if not self.text is None:
			self.data2(data)
		else:
			self.text = data


	def comment(self, data):
		self.doc_value_add(self.doc_node_add(8), 8, data)

	def pi(self, target, data):
		pi = self.doc_node_add(7)
		self.doc_value_add(pi, 0, target)
		self.doc_value_add(pi, 7, data)

	def close(self):
		self.doc_finalize()
