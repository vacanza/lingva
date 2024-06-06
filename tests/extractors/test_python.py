try:
    from unittest import mock
except ImportError:
    import mock

import io
import warnings

import pytest

from lingva.extractors.python import PythonExtractor

python_extractor = PythonExtractor()
source = None


@pytest.fixture
def fake_source(request):
    patcher = mock.patch(
        "lingva.extractors.python._open", side_effect=lambda *a: io.StringIO(source)
    )
    patcher.start()
    request.addfinalizer(patcher.stop)


@pytest.mark.usefixtures("fake_source")
def test_syntax_error():
    global source
    options = mock.Mock()
    options.keywords = []
    source = """def class xya _(u'føo' 1)"""
    with pytest.raises(SystemExit):
        generator = python_extractor("filename", options)
        list(generator)


@pytest.mark.usefixtures("fake_source")
def test_multiline_string():
    global source
    options = mock.Mock()
    options.keywords = []
    source = """_(u'őne two '\n'three')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].msgid == "őne two three"


@pytest.mark.usefixtures("fake_source")
def test_plural():
    global source
    options = mock.Mock()
    options.keywords = []
    source = """ngettext(u'one côw', u'%d cows', 5)"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].msgid == "one côw"
    assert messages[0].msgid_plural == "%d cows"


@pytest.mark.usefixtures("fake_source")
def test_translationstring_parameters():
    global source
    options = mock.Mock()
    options.keywords = []
    source = """_(u'msgid', default=u'Canonical text')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].msgctxt is None
    assert messages[0].msgid == "msgid"
    assert messages[0].comment == "Default: Canonical text"


@pytest.mark.usefixtures("fake_source")
def test_translationstring_context():
    global source
    options = mock.Mock()
    options.keywords = []
    source = """_(u'Canonical text', context='button')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].msgctxt == "button"
    assert messages[0].msgid == "Canonical text"


@pytest.mark.usefixtures("fake_source")
def test_keyword():
    global source
    options = mock.Mock()
    options.keywords = ["other"]
    source = """other("Some message")"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1


@pytest.mark.usefixtures("fake_source")
def test_function_call_in_keyword():
    global source
    options = mock.Mock()
    options.keywords = ["other"]
    source = """other(six.u('word'))"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 0


@pytest.mark.usefixtures("fake_source")
def test_use_lineno_parameter():
    global source
    options = mock.Mock()
    options.keywords = []
    source = """_(u'word')"""
    messages = list(python_extractor("filename", options, lineno=5))
    assert len(messages) == 1
    assert messages[0].location[1] == 6


@pytest.mark.usefixtures("fake_source")
def test_skip_comments():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = None
    source = """# source comment\n_(u'word')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].comment == ""


@pytest.mark.usefixtures("fake_source")
def test_include_all_comments():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = True
    source = """# source comment\n_(u'word')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].comment == "source comment"


@pytest.mark.usefixtures("fake_source")
def test_tagged_comment_on_previous_line():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = "I18N:"
    source = """# I18N: source comment\n_(u'word')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].comment == "source comment"


@pytest.mark.usefixtures("fake_source")
def test_tagged_comment_on_same_line():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = "I18N:"
    source = """_('word')  # I18N: source comment"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].comment == "source comment"


@pytest.mark.usefixtures("fake_source")
def test_tagged_multiline_comment():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = "I18N:"
    source = """# I18N: one\n# I18N: two\n_(u'word')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].comment == "one two"


@pytest.mark.usefixtures("fake_source")
def test_flags_in_comment():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = "I18N:"
    source = """# I18N: [markdown-format,fuzzy] Comment\n_(u'word')"""
    messages = list(python_extractor("filename", options))
    assert messages[0].flags == ["markdown-format", "fuzzy"]
    assert messages[0].comment == "Comment"


@pytest.mark.usefixtures("fake_source")
def test_comment_and_default_value():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = True
    source = """# source comment\n_(u'key', default='word')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].comment == "Default: word\nsource comment"


@pytest.mark.usefixtures("fake_source")
def test_domain_filter():
    global source
    options = mock.Mock()
    options.keywords = []
    options.domain = "other"
    source = """dgettext('mydomain', 'word')"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 0
    options.domain = "mydomain"
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1


@pytest.mark.usefixtures("fake_source")
def test_dict_argument():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = "I18N:"
    source = """_('word', mapping={'foo': 2})"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].msgid == "word"


@pytest.mark.usefixtures("fake_source")
def test_function_argument():
    global source
    options = mock.Mock()
    options.keywords = []
    options.comment_tag = "I18N:"
    source = """_('word', func('foo', 2))"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 1
    assert messages[0].msgid == "word"


@pytest.mark.usefixtures("fake_source")
def test_dot_operator_in_parameter():
    global source
    options = mock.Mock()
    options.keywords = []
    source = """self._[lang].gettext(item.name)"""
    messages = list(python_extractor("filename", options))
    assert len(messages) == 0


def test_bytes_input():
    # Backwards compatibility for plugins that call the Python extractor with
    # bytes input.
    input = b'_("word")'
    options = mock.Mock()
    options.keywords = []
    with mock.patch("lingva.extractors.python._open", side_effect=lambda *a: io.BytesIO(input)):
        with warnings.catch_warnings(record=True) as ctx:
            messages = list(python_extractor("filename", options))

        assert (
            str(ctx[0].message) == "Python extractor called with bytes input. "
            "Please update your plugin to submit unicode instead."
        )
        assert len(messages) == 1
        assert messages[0].msgid == "word"
