# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'COFFEA FCC Analyses'
copyright = 'Prayag Yadav'
author = 'Prayag Yadav'
release = '0.1'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'sphinx_rtd_theme'
html_theme = 'sphinx_nefertiti'
html_static_path = ['_static']

# -- Theme options ------------------------------------------------------------
# https://sphinx-nefertiti.readthedocs.io/en/latest/quick-start.html#customize-the-theme
html_theme_options = {
  "repository_name": "prayagyadav/coffea-fcc-analyses",
  "repository_url": "https://github.com/prayagyadav/coffea-fcc-analyses",
  "footer_links": ",".join([
    "Documentation|https://prayagyadav.github.io/coffea-fcc-analyses",
    "Repository|https://github.com/prayagyadav/coffea-fcc-analyses",
    "Issues|https://github.com/prayagyadav/coffea-fcc-analyses/issues",
    "COFFEA|https://github.com/CoffeaTeam/coffea",
    "FCCAnalyses|https://github.com/HEP-FCC/FCCAnalyses"
  ])
}
