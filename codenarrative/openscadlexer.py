from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


class OpenScadLexer(RegexLexer):
    name = "OpenSCAD"
    aliases = ["openscad"]
    filenames = ["*.scad"]

    tokens = {
        "root": [
            (r"[^\S\n]+", Text),
            (r"\n", Text),
            (r"//(\n|[\w\W]*?[^\\]\n)", Comment.Singleline),  # CommentSingle?
            (r"/(\\\n)?[*][\w\W]*?[*](\\\n)?/", Comment.Mutliline),  # CommentMultiline
            (r"/(\\\n)?[*][\w\W]*", Comment.Mutliline),  # CommentMultiline
            (r"[{}\[\]\(\),;:]", Punctuation),
            (r"[*!#%\-+=?/]", Operator),
            (r"&lt;|&lt;=|==|!=|&gt;=|&gt;|&amp;&amp;|\|\|", Operator),
            (r"\$(f[asn]|t|vp[rtd]|children)", Operator),
            (r"(undef|PI)\b", Keyword.Constant),
            (
                r"(use|include)((?:\s|\\\\s)+)",
                bygroups(Keyword.Namespace, Text),
                "includes",
            ),
            (
                r"(module)(\s*)([^\s\(]+)",
                bygroups(Keyword.Namespace, Text, Name.Namespace),
            ),
            (
                r"(function)(\s*)([^\s\(]+)",
                bygroups(Keyword.Declaration, Text, Name.Function),
            ),
            (r"\b(true|false)\b", Literal),
            (
                r"\b(function|module|include|use|for|intersection_for|if|else|return)\b",
                Keyword,
            ),
            (
                r"\b(circle|square|polygon|text|sphere|cube|cylinder|polyhedron|translate|rotate|scale|resize|mirror|multmatrix|color|offset|hull|minkowski|union|difference|intersection|abs|sign|sin|cos|tan|acos|asin|atan|atan2|floor|round|ceil|ln|log|pow|sqrt|exp|rands|min|max|concat|lookup|str|chr|search|version|version_num|norm|cross|parent_module|echo|import|import_dxf|dxf_linear_extrude|linear_extrude|rotate_extrude|surface|projection|render|dxf_cross|dxf_dim|let|assign|len)\b",
                Name.Builtin,
            ),
            (r"\bchildren\b", Name.Builtin.Pseudo),
            (r"&#34;(\\\\|\\&#34;|[^&#34;])*&#34;", Literal.StringDouble),
            (r"-?\d+(\.\d+)?(e[+-]?\d+)?", Literal.Number),
            (r"[a-zA-Z_]\w*", Name),
        ],
        "includes": [
            (
                r"(&lt;)([^&gt;]*)(&gt;)",
                bygroups(Punctuation, Comment.PreprocFile, Punctuation),
            ),
        ],
    }
