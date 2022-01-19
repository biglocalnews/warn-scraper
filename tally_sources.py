import us
import warn
import jinja2
from pathlib import Path

this_dir = Path(__file__).parent
loader = jinja2.FileSystemLoader(searchpath=this_dir / "docs" / "_templates/")
env = jinja2.Environment(loader=loader)


def main():
    """Update sources dashboard."""
    print("Tallying sources")

    scraper_list = warn.utils.get_all_states()
    print(f"{len(scraper_list)} scrapers found")

    docs_dir = this_dir / "scrapers"
    has_docs = [f.stem for f in docs_dir.glob("*.md") if f.stem in scraper_list]
    print(f"{len(has_docs)} scrapers have docs")

    haves, have_nots = [], []
    target_list = us.states.STATES_AND_TERRITORIES + [us.states.DC]
    for t in target_list:
        state = t.__dict__
        abbr = state["abbr"].lower()
        if abbr in scraper_list:
            state["has_docs"] = abbr in has_docs
            haves.append(state)
        else:
            state["has_docs"] = False
            have_nots.append(state)
    print(f"{len(haves)} states and territories have a scraper")
    print(f"{len(have_nots)} states and territories do not have a scraper")

    context = {
        "haves": haves,
        "have_nots": have_nots,
        "targets": target_list,
    }
    template = env.get_template("sources.md")
    md = template.render(**context)

    with open(this_dir / "docs" / "sources.md", "w") as fh:
        fh.write(md)


if __name__ == "__main__":
    main()
