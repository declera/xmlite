xquery version "1.0";

declare default element namespace "declera:xmlite";
declare namespace c="declera:code";

(: String interpolation :)

declare function local:interpolate-string($template as node(), $ctx as node()){
    string-join(local:interpolate-string-02(element c:code {local:interpolate-string-01($template, $ctx)}, '&#x0A;'), '')
};

declare function local:interpolate-string-01($template as node(), $ctx as node()){
    let $text := replace($template/text()[1], '[^&#x0A;]*([&#x0A;].*)', '$1', 's'),
        $text-nl := replace($text, '([&#x0A;][&#x20;&#x09;]*).+', '$1', 's')
    for $item at $item-ix in $template/node()
        return typeswitch($item)
            case element(suffix)
                return element c:text {$ctx/view/@suffix/string()}
            case element(axis-relation-sql)
                return (
                    element c:text {'and '},
                    element c:slot {
                        local:interpolate-string-01($ctx/view/axis-node-join/axis-relation/sql, $ctx)
                        }
                    )
            case text()
                return 
                    let $lines := tokenize($item, $text-nl),
                        $lines2 := if($item-ix = 1 and string-length($lines[1]) = 0) then subsequence($lines, 2) else $lines
                        for $s at $ix in $lines2
                            return (
                                if ($ix = 1) then () else element c:nl {},
                                element c:text {$s}
                                )
            default
                return ()
};

declare function local:interpolate-string-02($code as node(), $nl as xs:string){
    for $item in $code/node()
        return typeswitch($item)
            case element(c:nl)
                return $nl
            case element(c:text)
                return $item/string()
            case element(c:slot)
                return
                    let $indent := local:string-indent($item/preceding::c:nl[1]/following::c:text[1])
                        return (
                            local:interpolate-string-02($item, concat('&#x0A;', $indent))
                            )
            default
                return ()
};

declare function local:string-indent($s as xs:string){
    if (matches($s, '[&#x20;&#x09;]+'))
        then replace($s, '([&#x20;&#x09;]+).*', '$1')
        else ''
};

(: Views :)

declare variable $root := /*[1];
declare function local:views(){
    let $delimiter := ''
    for $axis at $ix in $root//axis
        let $template := $axis/ancestor::*[view-template][1]/view-template 
        return (
            if ($ix = 1) then () else $delimiter,
            local:interpolate-string($template, $axis)
            )
};

local:views()
