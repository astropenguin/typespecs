copyright = "2025 Akio Taniguchi"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
html_static_path = ["_static"]
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "github_url": "https://github.com/astropenguin/typespecs",
    "logo": {"text": "typespecs"},
    "navbar_end": [
        "version-switcher",
        "theme-switcher",
        "navbar-icon-links",
    ],
    "switcher": {
        "json_url": "https://astropenguin.github.io/typespecs/_static/switcher.json",
        "version_match": "1.0.0rc3",
    },
}
