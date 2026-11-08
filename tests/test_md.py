import pytest

from warn.scrapers import md

HEADER_NEW = (
    "<tr><th>Notice Date</th><th>NAICS Code</th><th>Company</th><th>Location</th>"
    "<th>Local Area</th><th>Total Employees</th><th>Effective Date</th><th>Type</th></tr>"
)
HEADER_OLD = HEADER_NEW.replace("Local Area", "WIA Code").replace(
    "<th>Type</th>", "<th>Type Code</th>"
)
KEY = (
    "<p>Local Area Codes 1. A.A. CO. 2. BALTO. CO. 3. BALTO. CITY 4. FREDERICK 5. LOWER SHORE "
    "6. MID-MD. 7. MONTGOMERY 8. PRINCE GEORGE'S 9. SOUTHERN MARYLAND 10. SUSQUEHANNA 11. UPPER SHORE "
    "12. WESTERN MARYLAND 13. STATEWIDE Type Codes 1. PLANT CLOSURE 2. MASS LAYOFF Download 2020 WARN Log</p>"
)


def page(header, rows, key=""):
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<html><body>{key}<table>{header}{body}</table></body></html>"


NEW_ROW = [
    "11/03/2026",
    "531311",
    "A &amp; G Management",
    "Glen Burnie",
    "Anne Arundel",
    "120",
    "01/03/2027",
    "Mass Layoff",
]
OLD_ROW = ["1/10/2020", "452210", "Macy's", "Salisbury", "5", "80", "3/30/2020", "1"]
COLS = md.OUTPUT_COLUMNS


def as_dict(row):
    return dict(zip(COLS, row))


def test_new_style_page_keeps_names_and_leaves_code_columns_empty():
    (row,) = md.parse_page(page(HEADER_NEW, [NEW_ROW]))
    r = as_dict(row)
    assert (
        r["Local Area"] == "Anne Arundel"
        and r["Type"] == "Mass Layoff"
        and r["Company"] == "A & G Management"
    )
    assert r["WIA Code"] == "" and r["Type Code"] == ""


def test_old_style_page_decodes_codes_from_the_pages_own_key_and_keeps_the_codes():
    (row,) = md.parse_page(page(HEADER_OLD, [OLD_ROW], KEY))
    r = as_dict(row)
    assert r["Local Area"] == "LOWER SHORE" and r["WIA Code"] == "5"
    assert r["Type"] == "PLANT CLOSURE" and r["Type Code"] == "1"
    assert (
        r["Notice Date"] == "1/10/2020"
        and r["Total Employees"] == "80"
        and r["Effective Date"] == "3/30/2020"
    )


def test_each_page_is_read_with_its_own_header_so_columns_do_not_slide():
    new = as_dict(md.parse_page(page(HEADER_NEW, [NEW_ROW]))[0])
    old = as_dict(md.parse_page(page(HEADER_OLD, [OLD_ROW], KEY))[0])
    # the old logic put the old page's numeric codes under Local Area and Type; neither is numeric now
    assert not new["Local Area"].isdigit() and not old["Local Area"].isdigit()
    assert not old["Type"].isdigit()


def test_several_codes_and_notes_are_decoded_and_odd_values_keep_their_raw_text():
    rows = [
        [
            "1/1/2021",
            "1",
            "Multi",
            "x",
            "7,8",
            "9",
            "2/1/2021",
            "2 (Possibly turning into a closure)",
        ],
        [
            "1/2/2021",
            "2",
            "Amp",
            "x",
            "7 & 8",
            "9",
            "2/1/2021",
            "1 *Note-An update to the earlier WARN",
        ],
        [
            "1/3/2021",
            "3",
            "Various",
            "x",
            "Various",
            "9",
            "2/1/2021",
            "Unsure at this time",
        ],
        [
            "1/4/2021",
            "4",
            "Free text",
            "x",
            "3",
            "9",
            "2/1/2021",
            "6 week temporary lay off",
        ],
    ]
    out = [as_dict(r) for r in md.parse_page(page(HEADER_OLD, rows, KEY))]
    assert out[0]["Local Area"] == "MONTGOMERY / PRINCE GEORGE'S"
    assert out[0]["Type"] == "MASS LAYOFF (Possibly turning into a closure)"
    assert out[1]["Local Area"] == "MONTGOMERY / PRINCE GEORGE'S"
    assert out[1]["Type"] == "PLANT CLOSURE *Note-An update to the earlier WARN"
    assert out[2]["Local Area"] == "" and out[2]["WIA Code"] == "Various"  # not guessed
    assert (
        out[2]["Type"] == "" and out[2]["Type Code"] == "Unsure at this time"
    )  # raw text kept
    assert out[3]["Local Area"] == "BALTO. CITY"
    assert (
        out[3]["Type"] == "" and out[3]["Type Code"] == "6 week temporary lay off"
    )  # "6" is not in the key


def test_an_unrecognized_column_raises_instead_of_misaligning_data():
    header = HEADER_NEW.replace("Local Area", "County")
    with pytest.raises(ValueError, match="Unrecognized Maryland WARN column"):
        md.parse_page(page(header, [NEW_ROW]))


def test_a_row_with_the_wrong_number_of_cells_raises():
    with pytest.raises(ValueError, match="cells"):
        md.parse_page(page(HEADER_NEW, [NEW_ROW[:-1]]))


def test_a_row_whose_tr_tag_is_missing_is_still_read():
    # Maryland's 2015 page has a row of cells with no <tr>; browsers and html5lib treat it as a row
    cells = "".join(f"<td>{c}</td>" for c in OLD_ROW)
    html = f"<html><body>{KEY}<table>{HEADER_OLD}<tr><td>1/1/2020</td><td>1</td><td>A</td><td>x</td><td>1</td><td>1</td><td>2/1/2020</td><td>1</td></tr>{cells}</table></body></html>"
    assert len(md.parse_page(html)) == 2
