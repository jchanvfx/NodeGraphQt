"""Support different light and dark mode logos.

By default, Sphinx provides ``html_logo`` as an option
to add a logo to your documentation project.

The Awesome Theme lets you define separate logos for light and dark mode
via theme options:

.. code-block:: python

   html_theme_options = {
       "logo_light": "<path>/<filename>",
       "logo_dark": "<path>/<filename>"
   }

Provide a path relative to the Sphinx configuration directory (with the :file:`conf.py` file).

:copyright: Copyright Kai Welke.
:license: MIT, see LICENSE for details
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx.util import isurl, logging
from sphinx.util.fileutil import copy_asset_file

logger = logging.getLogger(__name__)


def get_theme_options(app: Sphinx) -> Any:
    """Return theme options for the application.

    Adapted from the ``pydata_sphinx_theme``.
    https://github.com/pydata/pydata-sphinx-theme/blob/f15ecfed59a2a5096c05496a3d817fef4ef9a0af/src/pydata_sphinx_theme/utils.py
    """
    if hasattr(app.builder, "theme_options"):
        return app.builder.theme_options
    elif hasattr(app.config, "html_theme_options"):
        return app.config.html_theme_options
    else:
        return {}


def update_config(app: Sphinx) -> None:
    """Update the configuration, handling the ``builder-inited`` event.

    Adapted from the ``pydata_sphinx_theme``:
    https://github.com/pydata/pydata-sphinx-theme/blob/f15ecfed59a2a5096c05496a3d817fef4ef9a0af/src/pydata_sphinx_theme/__init__.py
    """
    theme_options = get_theme_options(app)

    # Check logo config
    dark_logo = theme_options.get("logo_dark")
    light_logo = theme_options.get("logo_light")
    if app.config.html_logo and (dark_logo or light_logo):
        # For the rendering of the logos, see ``header.html`` and ``sidebar.html``
        logger.warning(
            "Conflicting theme options: use either `html_logo` or `logo_light` and `logo_dark`."
        )
    if (
        (dark_logo and not light_logo) or (light_logo and not dark_logo)
    ) and not app.config.html_logo:
        logger.warning("You must use `logo_light` and `logo_dark` together.")


def setup_logo_path(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: Node,
) -> None:
    """Update the logo path for the templates."""
    theme_options = get_theme_options(app)
    for kind in ["dark", "light"]:
        logo = theme_options.get(f"logo_{kind}")
        if logo and not isurl(logo):
            context[f"theme_logo_{kind}"] = os.path.basename(logo)


def copy_logos(app: Sphinx, exc: Exception | None) -> None:
    """Copy the light and dark logos."""
    theme_options = get_theme_options(app)
    static_dir = str(Path(app.builder.outdir) / "_static")

    for kind in ["dark", "light"]:
        logo = theme_options.get(f"logo_{kind}")
        if logo and not isurl(logo):
            logo_path = Path(app.builder.confdir) / logo
            if not logo_path.exists():
                logger.warning("Path to logo %s does not exist.", logo)
            copy_asset_file(str(logo_path), static_dir)
