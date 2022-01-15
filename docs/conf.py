from datetime import datetime

extensions = ["myst_parser"]
templates_path = ["_templates"]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
master_doc = "index"

project = "warn-scraper"
year = datetime.now().year
copyright = f"{year} Big Local News"

exclude_patterns = ["_build"]

pygments_style = "sphinx"
