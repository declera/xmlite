from .doc import XmliteDocBuilder

from lxml import etree
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

	parser.close()
