import polib

from lingva.extract import POEntry, POFile, identical, read_config, strip_linenumbers
from lingva.extractors import EXTENSIONS, register_extractors

STRIPPED_LINENUMBERS_PO = """\
#: file.txt
msgid "A"
msgstr ""
"""


class Test_identical:
    def test_ignore_metadata_differences(self):
        a = POFile()
        a.metadata["Last-Translator"] = "Jane"
        b = polib.POFile()
        b.metadata["Last-Translator"] = "Alice"
        assert identical(a, b)

    def test_identical_entries(self):
        a = POFile()
        b = polib.POFile()
        a.append(POEntry(msgid="id 1"))
        b.append(polib.POEntry(msgid="id 1"))
        assert identical(a, b)
        a.append(POEntry(msgid="id 1", msgctxt="form"))
        assert not identical(a, b)
        b.append(polib.POEntry(msgid="id 1", msgctxt="form"))
        assert identical(a, b)

    def test_comment_change(self):
        a = POFile()
        b = polib.POFile()
        a.append(POEntry(msgid="id"))
        a[0]._comments.append("Comment")
        b.append(polib.POEntry(msgid="id"))
        assert not identical(a, b)
        b[0].comment = "Comment"
        assert identical(a, b)

    def test_tcomment_change(self):
        a = POFile()
        b = polib.POFile()
        a.append(POEntry(msgid="id"))
        a[0]._tcomments.append("Comment")
        b.append(polib.POEntry(msgid="id"))
        assert not identical(a, b)
        b[0].tcomment = "Comment"
        assert identical(a, b)

    def test_ignore_comment_whitespace_change(self):
        a = POFile()
        b = polib.POFile()
        a.append(POEntry(msgid="id"))
        a[0]._comments.append("Comment one")
        b.append(polib.POEntry(msgid="id"))
        b[0].comment = "Comment\none"
        assert identical(a, b)

    def test_strip_linenumbers(self):
        a = POFile()
        b = polib.pofile(STRIPPED_LINENUMBERS_PO)
        a.append(POEntry(msgid="A", occurrences=[("file.txt", "1")]))
        for entry in a:
            strip_linenumbers(entry)
        assert identical(a, b)

    def test_read_config(self):
        assert ".html" not in EXTENSIONS

        register_extractors()
        read_config(open("tests/data/test_config.cfg"))
        assert EXTENSIONS[".html"] == "xml"
