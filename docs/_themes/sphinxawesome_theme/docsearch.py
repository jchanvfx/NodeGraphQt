"""Add Algolia DocSearch to Sphinx.

This extension replaces the built-in search in Sphinx with Algolia DocSearch.
To load this extension, add:

.. code-block:: python
   :caption: |conf|

   extensions += ["sphinxawesome_theme.docsearch"]

:copyright: Kai Welke.
:license: MIT, see LICENSE for details
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx.builders.dirhtml import DirectoryHTMLBuilder
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.config import Config
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.display import progress_message

from . import __version__

logger = logging.getLogger(__name__)


@dataclass
class DocSearchConfig:
    """Configuration options for DocSearch.

    This class defines and documents the configuration options for the :py:mod:`sphinxawesome_theme.docsearch` extension.
    To configure DocSearch, you must use regular Python variables. For example:

    .. code-block:: python
       :caption: |conf|

       from sphinxawesome_theme.docsearch import DocSearchConfig

       config = DocSearchConfig(
           docsearch_app_id="DOCSEARCH_APP_ID"
           # Other options
       )

       docsearch_app_id = config.docsearch_app_id
    """

    docsearch_app_id: str
    """Your Algolia DocSearch application ID.

    You **must** provide an application ID or DocSearch won't work.
    """

    docsearch_api_key: str
    """Your Algolia DocSearch Search API key.

    You **must** provide your search API key or DocSearch won't work.

    .. caution::

       Don't expose your write API key.
    """

    docsearch_index_name: str
    """Your Algolia DocSearch index name.

    You **must** provide an index name or DocSearch won't work.
    """

    docsearch_container: str = "#docsearch"
    """A CSS selector where the DocSearch UI should be injected."""

    docsearch_placeholder: str | None = None
    """A placeholder for the search input.

    By default, DocSearch uses *Search docs*.
    """

    docsearch_initial_query: str | None = None
    """If you want to perform a search before the user starts typing."""

    docsearch_search_parameter: str | None = None
    """If you want to add `Algolia search parameter <https://www.algolia.com/doc/api-reference/search-api-parameters/>`_."""

    docsearch_missing_results_url: str | None = None
    """A URL for letting users send you feedback about your search.

    You can use the current query in the URL as ``${query}``. For example:

    .. code-block:: python

       docsearch_missing_results_url = "https://github.com/example/docs/issues/new?title=${query}"
    """


@progress_message("DocSearch: check config")
def check_config(app: Sphinx, config: Config) -> None:
    """Set up Algolia DocSearch.

    Log warnings if any of these configuration options are missing:

    - ``docsearch_app_id``
    - ``docsearch_api_key``
    - ``docsearch_index_name``
    """
    if not config.docsearch_app_id:
        logger.warning(
            __("You must provide your Algolia application ID for DocSearch to work.")
        )
    if not config.docsearch_api_key:
        logger.warning(
            __("You must provide your Algolia search API key for DocSearch to work.")
        )
    if not config.docsearch_index_name:
        logger.warning(
            __("You must provide your Algolia index name for DocSearch to work.")
        )


@progress_message("DocSearch: add assets")
def add_docsearch_assets(app: Sphinx, config: Config) -> None:
    """Add the docsearch.css file for DocSearch."""
    app.add_css_file("docsearch.css", priority=150)
    # TODO: add_js_file (currently in `layout.html` I think)


def update_global_context(app: Sphinx, doctree: Node, docname: str) -> None:
    """Update global context with DocSearch configuration."""
    if hasattr(app.builder, "globalcontext"):
        app.builder.globalcontext["docsearch"] = True
        app.builder.globalcontext["docsearch_app_id"] = app.config.docsearch_app_id
        app.builder.globalcontext["docsearch_api_key"] = app.config.docsearch_api_key
        app.builder.globalcontext[
            "docsearch_index_name"
        ] = app.config.docsearch_index_name
        app.builder.globalcontext[
            "docsearch_container"
        ] = app.config.docsearch_container
        app.builder.globalcontext[
            "docsearch_initial_query"
        ] = app.config.docsearch_initial_query
        app.builder.globalcontext[
            "docsearch_placeholder"
        ] = app.config.docsearch_placeholder
        app.builder.globalcontext[
            "docsearch_search_parameter"
        ] = app.config.docsearch_search_parameter
        app.builder.globalcontext[
            "docsearch_missing_results_url"
        ] = app.config.docsearch_missing_results_url


def remove_script_files(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: Node,
) -> None:
    """Remove Sphinx JavaScript files when using DocSearch."""
    context["script_files"].remove("_static/documentation_options.js")
    context["script_files"].remove("_static/doctools.js")
    context["script_files"].remove("_static/sphinx_highlight.js")


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the extension."""
    # Get the configuration from a single-source of truth
    # This makes it easy to document.
    for option in fields(DocSearchConfig):
        default = option.default if isinstance(option.default, str) else ""
        app.add_config_value(option.name, default=default, rebuild="html", types=(str))

    app.connect("config-inited", check_config)
    app.connect("config-inited", add_docsearch_assets)
    app.connect("doctree-resolved", update_global_context)
    app.connect("html-page-context", remove_script_files)

    # Disable built-in search
    StandaloneHTMLBuilder.search = False
    DirectoryHTMLBuilder.search = False

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
