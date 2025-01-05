from importlib.metadata import entry_points

from . import EXTRACTORS, Extractor, Message, check_c_format, check_python_format, update_keywords
from .python import KEYWORDS, parse_keyword


class BabelExtractor(Extractor):
    extensions = []
    extractor = None
    default_config = {
        "comment-tags": "",
    }

    def __call__(self, filename, options, fileobj=None, firstline=0):
        self.keywords = KEYWORDS.copy()
        update_keywords(self.keywords, options.keywords)
        if fileobj is None:
            fileobj = open(filename, "rb")
        comment_tags = self.config["comment-tags"].split()
        messages = self.extractor(fileobj, list(self.keywords.keys()), comment_tags, self.config)
        for lineno, function, args, comment in messages:
            if not isinstance(args, (list, tuple)):
                args = [args]
            if function in self.keywords:
                args = [(None, a, lineno) for a in args]
                (domain, msgctxt, msgid, msgid_plural, c) = parse_keyword(
                    args, self.keywords[function], filename, lineno
                )
                if c:
                    comment.append(c)
            else:
                msgid = args[0]
                domain = msgctxt = msgid_plural = None

            if domain and self.options.domain and domain != self.options.domain:
                continue
            comment = " ".join(comment)
            flags = []
            check_c_format(msgid, flags)
            check_python_format(msgid, flags)
            yield Message(
                msgctxt,
                msgid,
                msgid_plural,
                flags,
                comment,
                "",
                (filename, firstline + lineno),
            )


def register_babel_plugins():
    try:
        babel_entry_points = entry_points(group="babel.extractors")
    except TypeError:  # <= Python 3.9
        babel_entry_points = entry_points()["babel.extractors"]

    for entry_point in babel_entry_points:
        try:
            extractor = entry_point.load()
        except ModuleNotFoundError:
            extractor = None
        if extractor:
            name = entry_point.name
            cls = type(
                "BabelExtractor_%s" % name,
                (BabelExtractor, object),
                {
                    "extractor": staticmethod(extractor),
                    "__doc__": extractor.__doc__.splitlines()[0],
                },
            )
            EXTRACTORS["babel-%s" % name] = cls()
