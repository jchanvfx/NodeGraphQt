"""Check for deprecated options.

This extension checks if you're using a deprecated option from the
sphinxawesome_theme from a version < 5.0.

Theme options in the ``html_theme_options`` dictionary are handled automatically.
Regular configuration options however need to be checked separately,
because the HTML theme is loaded _after_ the configuration is handled,
and extensions are already processed.

To load this extension, add:

.. code-block:: python
   :caption: |conf|

   extensions += ["sphinxawesome_theme.deprecated"]

:copyright: Kai Welke.
:license: MIT, see LICENSE for details
"""
from __future__ import annotations

from typing import Any

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

from . import __version__

logger = logging.getLogger(__name__)


def check_deprecated(app: Sphinx, config: Config) -> None:  # noqa: C901
    """Check the Sphinx configuration for the deprecated options and migrate them automatically if possible."""
    raw = config._raw_config
    found_deprecated = False

    if "html_collapsible_definitions" in raw:
        logger.warning(
            "`html_collapsible_definitions` is deprecated. "
            "Use the `sphinx-design` extension instead."
        )
        found_deprecated = True

    if "html_awesome_headerlinks" in raw:
        logger.warning(
            "`html_awesome_headerlinks` is deprecated. "
            "Use `html_theme_options = {'awesome_headerlinks: True '} instead."
        )
        config.html_theme_options["awesome_headerlinks"] = raw[
            "html_awesome_headerlinks"
        ]
        found_deprecated = True

    if "html_awesome_external_links" in raw:
        logger.warning(
            "`html_awesome_external_links` is deprecated. "
            "Use `html_theme_options = {'awesome_external_links: True '} instead."
        )
        config.html_theme_options["awesome_external_links"] = raw[
            "html_awesome_external_links"
        ]
        found_deprecated = True

    # Since this won't have any effect, it shouldn't be a warning.
    if "html_awesome_code_headers" in raw:
        logger.info(
            "`html_awesome_code_headers` is deprecated. "
            "You can remove it from your Sphinx configuration."
        )
        found_deprecated = True

    if "html_awesome_docsearch" in raw:
        logger.warning(
            "`html_awesome_docsearch` is deprecated. "
            "Use the bundled `sphinxawesome_theme.docsearch` extension instead."
        )
        found_deprecated = True

        if raw["html_awesome_docsearch"]:
            app.setup_extension("sphinxawesome_theme.docsearch")

    if "docsearch_config" in raw:
        logger.warning(
            "Using the `docsearch_config` dictionary is deprecated. "
            "Load the bundled `sphinxawesome_theme.docsearch` extension and configure DocSearch with `docsearch_*` variables."
        )
        found_deprecated = True

        # Only process the docsearch options if the user actually wants DocSearch
        if (
            "sphinxawesome_theme.docsearch" in app.extensions
            and raw["docsearch_config"]
            and raw["html_awesome_docsearch"]
        ):
            ds_conf = raw["docsearch_config"]
            if "app_id" in ds_conf:
                config.docsearch_app_id = ds_conf["app_id"]  # type: ignore[attr-defined]

            if "api_key" in ds_conf:
                config.docsearch_api_key = ds_conf["api_key"]  # type: ignore[attr-defined]

            if "index_name" in ds_conf:
                config.docsearch_index_name = ds_conf["index_name"]  # type: ignore[attr-defined]

            if "container" in ds_conf:
                config.docsearch_container = ds_conf["container"]  # type: ignore[attr-defined]

    if found_deprecated is False:
        logger.info(
            "No deprecated options found. You can remove the `sphinxawesome_theme.deprecated` extension."
        )


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the extension."""
    if "sphinxawesome_theme" in app.config.extensions:
        logger.warning(
            "Including `sphinxawesome_theme` in your `extensions` is deprecated. "
            'Setting `html_theme = "sphinxawesome_theme"` is enough. '
            "You can load the optional `sphinxawesome_theme.docsearch` and `sphinxawesome_theme.highlighting` extensions."
        )
        app.setup_extension("sphinxawesome_theme.highlighting")
        app.setup_extension("sphinxawesome_theme.docsearch")

    # If we don't register these options, Sphinx ignores them when evaluating the `conf.py` file.
    app.add_config_value(
        name="html_collapsible_definitions", default=False, rebuild="html", types=(bool)
    )
    app.add_config_value(
        name="html_awesome_external_links", default=False, rebuild="html", types=(bool)
    )
    app.add_config_value(
        name="html_awesome_docsearch", default=False, rebuild="html", types=(bool)
    )
    app.add_config_value(
        name="docsearch_config", default={}, rebuild="html", types=(dict)
    )
    app.add_config_value(
        name="html_awesome_headerlinks", default=True, rebuild="html", types=(str)
    )
    app.add_config_value(
        name="html_awesome_code_headers", default=True, rebuild="html", types=(str)
    )

    app.connect("config-inited", check_deprecated)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
