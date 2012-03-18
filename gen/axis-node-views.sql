drop view if exists doc_node_ancestor;
create view doc_node_ancestor as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_ix in (select max(doc_ix) from doc_node where doc = base.doc and doc_ix < base.doc_ix group by doc_level)
						
;
		

drop view if exists doc_node_ancestor_or_self;
create view doc_node_ancestor_or_self as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_ix in (select max(doc_ix) from doc_node where doc = base.doc and doc_ix <= base.doc_ix group by doc_level)
						
;
		

drop view if exists doc_node_child;
create view doc_node_child as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_level = base.doc_level + 1
				and axis.doc_ix
					between base.doc_ix
						and coalesce(
							(select min(doc_ix) from doc_node where doc = base.doc and doc_level = base.doc_level and doc_ix > base.doc_ix),
							(select max(doc_ix) from doc_node where doc = base.doc)
							)
						
;
		

drop view if exists doc_node_descendant;
create view doc_node_descendant as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_ix
					between base.doc_ix + 1
						and coalesce(
							(select min(doc_ix) from doc_node where doc = base.doc and doc_level = base.doc_level and doc_ix > base.doc_ix),
							(select max(doc_ix) from doc_node where doc = base.doc)
							)
						
;
		

drop view if exists doc_node_descendant_or_self;
create view doc_node_descendant_or_self as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_ix
					between base.doc_ix
						and coalesce(
							(select min(doc_ix) from doc_node where doc = base.doc and doc_level = base.doc_level and doc_ix > base.doc_ix),
							(select max(doc_ix) from doc_node where doc = base.doc)
							)
						
;
		

drop view if exists doc_node_following;
create view doc_node_following as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_ix > base.doc_ix
						
;
		

drop view if exists doc_node_following_sibling;
create view doc_node_following_sibling as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_level = base.doc_level
				and axis.doc_ix
					between base.doc_ix + 1
						and coalesce(
							(select min(doc_ix) from doc_node where doc = base.doc and doc_level = base.doc_level - 1 and doc_ix > base.doc_ix),
							(select max(doc_ix) from doc_node where doc = base.doc)
							)
						
;
		

drop view if exists doc_node_parent;
create view doc_node_parent as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_ix = (select max(doc_ix) from doc_node where doc = base.doc and doc_level = base.doc_level - 1 and doc_ix < base.doc_ix)
						
;
		

drop view if exists doc_node_preceding;
create view doc_node_preceding as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_ix < base.doc_ix
						
;
		

drop view if exists doc_node_preceding_sibling;
create view doc_node_preceding_sibling as
	select
		base.doc_node base,

		axis.doc, axis.doc_node, axis.doc_type,

		axis.doc_ix, axis.doc_level,

		axis.prototype

		from doc_node base
			inner join doc_node axis
				on axis.doc = base.doc
				and axis.doc_level = base.doc_level
				and axis.doc_ix
					between (select max(doc_ix) + 1 from doc_node where doc = base.doc and doc_level = base.doc_level - 1 and doc_ix < base.doc_ix)
						and base.doc_ix
						
;
		

drop view if exists doc_node_self;
create view doc_node_self as
	select
		doc_node base,

		doc, doc_node, doc_type,

		doc_ix,	doc_level,

		prototype

		from doc_node base
;
		
