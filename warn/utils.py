import csv

import requests


def write_rows_to_csv(rows, output_path, mode="w"):
    """
    Write the provided list to the provided path as comma-separated values.

    Arguments:
    rows -- the list to be saved
    output_dir -- the Path were the result will be saved

    Keyword arguments:
    mode -- the mode to be used when opening the file (default 'w')
    """
    with open(output_path, mode, newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def write_dict_rows_to_csv(output_path, headers, rows, mode="w", extrasaction="raise"):
    """
    Write the provided dictionary to the provided path as comma-separated values.

    Arguments:
    output_path -- the Path were the result will be saved
    headers -- a list of the headers for the output file
    rows -- the dict to be saved

    Keyword arguments:
    mode -- the mode to be used when opening the file (default 'w')
    extrasaction -- what to do if the if a field isn't in the headers (default 'raise')
    """
    with open(output_path, mode, newline="") as f:
        # Create the writer object
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction=extrasaction)
        # If we are writing a new row ...
        if mode == "w":
            # ... drop in the headers
            writer.writeheader()
        # Loop through the dicts and write them in one by one.
        for row in rows:
            writer.writerow(row)


def download_file(url, local_path):
    """
    Download the provided URL.

    Arguments:
    url -- the hyperlink to download
    local_path -- the Path to save the file on disk

    Returns: the Path where the file was saved
    """
    # Get the URL
    with requests.get(url, stream=True) as r:
        # If there's no encoding, set it
        if r.encoding is None:
            r.encoding = "utf-8"
        # Open the local Path
        with open(local_path, "wb") as f:
            # Write out the file in little chunks
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    # Return the path
    return local_path
