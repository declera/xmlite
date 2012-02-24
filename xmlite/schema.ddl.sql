create table doc_type(
	doc_type integer primary key,
	qname text
);
create index doc_type_keyix on doc_type(qname);

create table doc(
	doc integer primary key,
	location text
);
create index doc_keyix on doc(location);


create table doc_node(
	doc_node integer primary key,
	doc integer references doc,

	doc_ix integer,
	doc_level integer,

	doc_type integer references doc_type,
	prototype integer
);

create index doc_node_ordix on doc_node(doc, doc_ix, doc_type);
create index doc_node_wavix on doc_node(doc, doc_level, doc_ix);

create table doc_ns(
	doc_ns integer primary key,
	doc_node integer references doc_node,
	prefix text,
	uri text
);
create index doc_ns_nodix on doc_ns(doc_node, prefix);

create table doc_value(
	doc_value integer primary key,
	doc_node integer references doc_node,
	doc_type integer references doc_type,
	value
);
create index doc_value_nodix on doc_node(doc_node, doc_type);

pragma journal_mode=wal;
