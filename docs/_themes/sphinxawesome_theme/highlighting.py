"""Add more highlighting options to Pygments.

This extension extends the Sphinx ``code-block``
directive with new options:

- ``:emphasize-added:``: highlight added lines
- ``:emphasize-removed:``: highlight removed lines
- ``:emphasize-text:``: highlight a single word, such as, a placeholder

To load this extension, add:

.. code-block:: python
   :caption: File: conf.py

   extensions += ["sphinxawesome_theme.highlighting"]

To achieve this, this extension makes a few larger changes:

1. Provide a new Sphinx directive: ``AwesomeCodeBlock``.
   This parses the additional options and passes them to the syntax highlighter.

2. Provide a new Pygments HTML formatter ``AwesomeHtmlFormatter``.
   This handles formatting the lines for added or removed options.
   This extension changes the output compared to the default Sphinx implementation.
   For example, each line is wrapped in a ``<span>`` element,
   and the whole code block is wrapped in a ``<pre><code>..`` element.
   For highlighted lines, this extension uses ``<mark>``, ``<ins>``, and ``<del>`` elements.

3. Define a new custom Pygments filter ``AwesomePlaceholders``,
   which wraps each encountered placeholder word in a ``Generic.Emphasized`` token,
   such that we can style placeholders by CSS.

4. Monkey-patch the ``PygmentsBridge.get_lexer`` method to apply the ``AwesomePlaceholders`` filter,
   if the option for it is present.

5. Monkey-patch the ``PygmentsBridge.highlight_block`` method to pass the option for highlighting text to the ``get_lexer`` method.

:copyright: Copyright Kai Welke.
:license: MIT, see LICENSE for details.
"""
from __future__ import annotations

import re
from typing import Any, Generator, Literal, Pattern, Tuple, Union

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives
from pygments.filter import Filter
from pygments.formatters import HtmlFormatter
from pygments.lexer import Lexer
from pygments.token import Generic, _TokenType
from pygments.util import get_list_opt
from sphinx.application import Sphinx
from sphinx.directives.code import CodeBlock
from sphinx.highlighting import PygmentsBridge
from sphinx.locale import __
from sphinx.util import logging, parselinenos

from . import __version__

logger = logging.getLogger(__name__)

# type alias
TokenType = Union[_TokenType, int]  # For Python 3.8
TokenStream = Generator[Tuple[TokenType, str], None, None]


def _replace_placeholders(
    ttype: _TokenType, value: str, regex: Pattern[str]
) -> TokenStream:
    """Replace every occurence of ``regex`` with ``Generic.Emph`` token."""
    last = 0
    for match in regex.finditer(value):
        start, end = match.start(), match.end()
        if start != last:
            yield ttype, value[last:start]
        yield Generic.Emph, value[start:end]
        last = end
    if last != len(value):
        yield ttype, value[last:]


# Without the comment, `mypy` throws a fit:
# Cannot subclass Filter, is type `Any`


class AwesomePlaceholders(Filter):  # type: ignore[misc]
    """A Pygments filter for marking up placeholder text.

    You can define the text to highlight with the ``hl_text`` option.
    To add the filter to a Pygments lexer, use the ``add_filter`` method:

    .. code-block:: python

       f = AwesomePlaceholders(hl_text=TEXT)
       lexer.add_filter(AwesomePlaceholders(hl_text=TEXT))

    For more information, see the `Pygments documentation <https://pygments.org/docs/quickstart/>`__.
    """

    def __init__(self: AwesomePlaceholders, **options: str) -> None:
        """Create an instance of the ``AwesomePlaceholders`` filter."""
        Filter.__init__(self, **options)
        placeholders = get_list_opt(options, "hl_text", [])
        self.placeholders_re = re.compile(
            r"|".join([re.escape(x) for x in placeholders if x])
        )

    def filter(
        self: AwesomePlaceholders, _lexer: Any, stream: TokenStream
    ) -> TokenStream:
        """Filter on all tokens.

        The ``lexer`` instance is required by the parent class, but isn't used here.
        """
        regex = self.placeholders_re
        for ttype, value in stream:
            yield from _replace_placeholders(ttype, value, regex)


class AwesomeHtmlFormatter(HtmlFormatter):  # type: ignore
    """Custom Pygments HTML formatter for highlighting added or removed lines.

    The method is similar to handling the ``hl_lines`` option in the regular HtmlFormatter.
    """

    def _get_line_numbers(
        self: AwesomeHtmlFormatter,
        options: dict[str, Any],
        which: Literal["hl_added", "hl_removed"],
    ) -> set[int]:
        """Get the lines to be added or removed."""
        line_numbers = set()
        for lineno in get_list_opt(options, which, []):
            try:
                line_numbers.add(int(lineno))
            except ValueError:
                pass
        return line_numbers

    def __init__(self: AwesomeHtmlFormatter, **options: Any) -> None:
        """Implement `hl_added` and `hl_removed` options.

        Also set the ``linespans`` and ``wrapcode`` options of the Pygments HTML formatter to ``True``.
        """
        self.added_lines = self._get_line_numbers(options, "hl_added")
        self.removed_lines = self._get_line_numbers(options, "hl_removed")

        # These options aren't compatible with `sphinx.ext.autodoc`
        # options["lineanchors"] = "code"
        options["linespans"] = "line"
        options["wrapcode"] = True

        super().__init__(**options)

    def _highlight_lines(
        self: AwesomeHtmlFormatter, tokensource: TokenStream
    ) -> TokenStream:
        """Highlight added, removed, and emphasized lines.

        In contrast to Pygments, use ``<mark>``, ``<ins>``, and ``<del>`` elements.
        """
        for i, (t, value) in enumerate(tokensource):
            if t != 1:
                yield t, value
            if i + 1 in self.hl_lines:
                yield 1, "<mark>%s</mark>" % value
            elif i + 1 in self.added_lines:
                yield 1, "<ins>%s</ins>" % value
            elif i + 1 in self.removed_lines:
                yield 1, "<del>%s</del>" % value
            else:
                yield 1, value

    def format_unencoded(
        self: AwesomeHtmlFormatter,
        tokensource: TokenStream,
        outfile: Any,
    ) -> None:
        """Overwrite method to handle emphasized, added, and removed lines.

        Unfortunately, the method doesn't extend easily, so I copy it from Pygments.
        """
        source = self._format_lines(tokensource)

        # As a special case, we wrap line numbers before line highlighting
        # so the line numbers get wrapped in the highlighting tag.
        if not self.nowrap and self.linenos == 2:
            source = self._wrap_inlinelinenos(source)

        # This is the only change I made from the original
        if self.hl_lines or self.added_lines or self.removed_lines:
            source = self._highlight_lines(source)

        if not self.nowrap:
            if self.lineanchors:
                source = self._wrap_lineanchors(source)
            if self.linespans:
                source = self._wrap_linespans(source)
            source = self.wrap(source)
            if self.linenos == 1:
                source = self._wrap_tablelinenos(source)
            source = self._wrap_div(source)
            if self.full:
                source = self._wrap_full(source, outfile)

        for _, piece in source:
            outfile.write(piece)


class AwesomeCodeBlock(CodeBlock):
    """An extension of the Sphinx ``code-block`` directive to handle additional options.

    - ``:emphasize-added:`` highlight added lines
    - ``:emphasize-removed:`` highlight removed lines
    - ``:emphasize-text:`` highlight placeholder text

    The job of the directive is to set the correct options to the ``literal_block`` node,
    which represents a code block in the parsed reStructuredText tree.
    When transforming the abstract tree to HTML,
    Sphinx passes these options to the ``highlight_block`` method,
    which is a wrapper around Pygments' ``highlight`` method.
    Handling these options is then a job of the ``AwesomePygmentsBridge``.
    """

    new_options = {
        "emphasize-added": directives.unchanged_required,
        "emphasize-removed": directives.unchanged_required,
        "emphasize-text": directives.unchanged_required,
    }

    option_spec = CodeBlock.option_spec
    option_spec.update(new_options)

    def _get_line_numbers(
        self: AwesomeCodeBlock, option: Literal["emphasize-added", "emphasize-removed"]
    ) -> list[int] | None:
        """Parse the line numbers for the ``:emphasize-added:`` and ``:emphasize-removed:`` options."""
        document = self.state.document
        location = self.state_machine.get_source_and_line(self.lineno)
        nlines = len(self.content)
        linespec = self.options.get(option)

        if not linespec:
            return None

        try:
            line_numbers = parselinenos(linespec, nlines)
            if any(i >= nlines for i in line_numbers):
                logger.warning(
                    __("line number spec is out of range(1-%d): %r")
                    % (nlines, linespec),
                    location=location,
                )
            return [i + 1 for i in line_numbers if i < nlines]
        except ValueError as err:
            return [document.reporter.warning(err, line=self.lineno)]

    def run(self: AwesomeCodeBlock) -> list[Node]:
        """Handle parsing extra options for highlighting."""
        literal_nodes = super().run()

        hl_added = self._get_line_numbers("emphasize-added")
        hl_removed = self._get_line_numbers("emphasize-removed")

        # `literal_nodes` is either `[literal_block]`, or `[caption, literal_block]`
        for node in literal_nodes:
            if isinstance(node, nodes.literal_block):
                extra_args = node.get("highlight_args", {})

                if hl_added is not None:
                    extra_args["hl_added"] = hl_added
                if hl_removed is not None:
                    extra_args["hl_removed"] = hl_removed
                if "emphasize-text" in self.options:
                    extra_args["hl_text"] = self.options["emphasize-text"]

        return literal_nodes


# These external references are needed, or you'll get a maximum recursion depth error
pygmentsbridge_get_lexer = PygmentsBridge.get_lexer
pygmentsbridge_highlight_block = PygmentsBridge.highlight_block


class AwesomePygmentsBridge(PygmentsBridge):
    """Monkey-patch the Pygments methods to handle highlighting placeholder text."""

    def get_lexer(
        self: AwesomePygmentsBridge,
        source: str,
        lang: str,
        opts: dict[str, Any] | None = None,
        force: bool = False,
        location: Any = None,
    ) -> Lexer:
        """Monkey-patch the ``PygmentsBridge.get_lexer`` method.

        Adds a filter to lexers if the ``hl_text`` option is present.
        """
        lexer = pygmentsbridge_get_lexer(self, source, lang, opts, force, location)

        if opts and "hl_text" in opts:
            lexer.add_filter(AwesomePlaceholders(hl_text=opts["hl_text"]))
        return lexer

    def highlight_block(
        self: AwesomePygmentsBridge,
        source: str,
        lang: str,
        opts: dict[str, Any] | None = None,
        force: bool = False,
        location: Any = None,
        **kwargs: Any,
    ) -> str:
        """Monkey-patch the ``PygmentsBridge.highlight_block`` method.

        This method is called, when Sphinx transforms the abstract document tree
        to HTML and encounters code blocks.
        The ``hl_text`` option is passed in the ``kwargs`` dictionary.
        For the ``get_lexer`` method, we need to pass it in the ``opts`` dictionary.
        """
        if opts is None:
            opts = {}

        hl_text = get_list_opt(kwargs, "hl_text", [])

        if hl_text:
            opts["hl_text"] = hl_text

        return pygmentsbridge_highlight_block(
            self, source, lang, opts, force, location, **kwargs
        )


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up this internal extension."""
    PygmentsBridge.html_formatter = AwesomeHtmlFormatter
    PygmentsBridge.get_lexer = AwesomePygmentsBridge.get_lexer  # type: ignore
    PygmentsBridge.highlight_block = (  # type: ignore
        AwesomePygmentsBridge.highlight_block  # type: ignore
    )
    directives.register_directive("code-block", AwesomeCodeBlock)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
