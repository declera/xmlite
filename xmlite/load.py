from lxml import etree
from .doc import XmliteDocBuilder, doc_walk

def FeedParser(db, location):
	return etree.XMLParser(target = XmliteDocBuilder(db, location))

def load_file(f, db, f_location = None):
	parser = FeedParser(db, f_location)
	while True:

		b = f.read(4096)
		if(len(b)):
			parser.feed(b)
		else:
			break

	return parser.close()

def db_xml(db, doc):
	handler = etree.TreeBuilder()
	doc_walk(db, doc, handler)
	return handler.close()

def db_xml_string(db, doc):
	return etree.tostring(db_xml(db, doc), pretty_print=True)
