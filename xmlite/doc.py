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

	def doc_node_add(self, qname, lplus = 0):
		self.ix += 1
		self.cnode_add.execute(
			"insert into doc_node(doc, doc_ix, doc_level, doc_type) values(?, ?, ?, ?)",
			(self.doc, self.ix, self.level + lplus, qname if type(qname) is int else self.doc_type_sget(qname))
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
	'''Builder with ET builder interface (start, end, data, ...)'''

	__slots__ = (
		'text' # accumulator keeping last text node, unless considered ignorable
	)

	def init(self):
		self.text = None

	def data2(self, data = None):
		if not len(self.text.lstrip()) == 0:
			self.doc_value_add(self.doc_node_add(3, 1), 3, self.text)
		self.text = data

	def start(self, qname, attrs, nsmap):
		if not self.text is None:
			self.data2()

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
		self.doc_value_add(self.doc_node_add(8, 1), 8, data)

	def pi(self, target, data):
		pi = self.doc_node_add(7, 1)
		self.doc_value_add(pi, 0, target)
		self.doc_value_add(pi, 7, data)

	def close(self):
		self.doc_finalize()
		return doc


def db_items(db, sql, *args):
	items = db.cursor()
	items.execute(sql, args)
	return items

def db_items_z(db, sql, *args):
	'''Row tuples for sql + on (None, None, ...)  tuple at the end'''
	items = db_items(db, sql, *args)
	for item in items:
		yield item
	yield (None,) * len(items.description)

try:
	from collections import OrderedDict as attrs_dict
except ImportError:
	attrs_dict = dict

def doc_walk(db, doc, handler):
	'''Walk doc nodes in parser style. i.e. calling the ET handler interface (start, end, data ...)'''

	nodes = db_items(db, '''
		select
			doc_node, doc_level, doc_type node_type,
			(select qname from doc_type where doc_type = node.doc_type) node_name
			from doc_node node
				where node.doc = ?
				order by node.doc_ix
	''', doc)

	attrs = attrs_dict() # Element attributes
	hcalls = [] # Handler methods (ip, data, comment) to be called after node items collecting
	values = db_items_z(db, '''
		select
			item.doc_node, item.doc_type, item.value,
			(select qname from doc_type where doc_type = item.doc_type) value_name
			from doc_node node
				inner join doc_value item
					on item.doc_node = node.doc_node
				where node.doc = ?
				order by node.doc_ix, item.doc_value
	''', doc)
	value_node, value_type, value, value_name = values.next()

	nsmap = attrs_dict() # Element: ns prefix, uri map
	nsmaps = db_items_z(db, '''
		select
			item.doc_node, item.prefix, item.uri
			from doc_node node
				inner join doc_ns item
					on item.doc_node = node.doc_node
				where node.doc = ?
				order by node.doc_ix, item.doc_ns
	''', doc)
	nsmap_node, ns_prefix, ns_uri = nsmaps.next()


	path = [] # Open elements stack
	for node, level, node_type, node_name in nodes:

		# NSMap
		while nsmap_node == node:
			nsmap[ns_prefix] = ns_uri
			nsmap_node, ns_prefix, ns_uri = nsmaps.next()

		# Attributes, PIs, Texts, Comments
		while value_node == node:
			if value_type > 8: # Attribute
				attrs[value_name] = value
			else:
				if value_type == 0: # PI (processing-instruction) target
					target = value
				elif value_type == 7:
					hcalls.append((handler.pi, (target, value)))
				elif value_type == 3:
					hcalls.append((handler.data, value))
				elif value_type == 8:
					hcalls.append((handler.comment, value))

			value_node, value_type, value, value_name = values.next()

		if node_type > 8: # Element

			# macro:close_elements
			ldelta = len(path) - level
			while ldelta > 0:
				handler.end(path.pop())
				ldelta -= 1

			handler.start(node_name, attrs, nsmap)
			path.append(node_name)
			nsmap.clear()
			attrs.clear()

		if hcalls:
			for hcall,arg in hcalls:
				if type(arg) is tuple:
					hcall(*arg)
				else:
					hcall(arg)
			hcalls = []

	# macro:close_elements
	ldelta = len(path) - 0
	while ldelta > 0:
		handler.end(path.pop())
		ldelta -= 1
