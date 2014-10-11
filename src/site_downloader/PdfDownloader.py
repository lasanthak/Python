import sys
import re
import os
import urllib.request
import urllib.error


def do(func, *args):
    result = func(*args)
    if not result:
        sys.exit(0)
    return result


def init(site_url, file_dir):
    if not os.path.exists(file_dir):
        print("Invalid file directory " + file_dir)
        return
    return True


def get_page_name(page_url, file_dir):
    file_name = page_url.split(sep="/")[-1]
    return file_dir + os.sep + file_name


def download(page_url, file_dir, overwrite=True):
    if not page_url:
        print("Invalid page url")
        return
    full_file_path = get_page_name(page_url, file_dir)
    if not overwrite and os.path.exists(full_file_path):
        print("File already exists, bailing out: " + full_file_path)
        return full_file_path
    print("Downloading " + page_url + " to " + full_file_path)
    try:
        httpResult = urllib.request.urlretrieve(page_url, full_file_path)
        # print(httpResult[1]["Content-Length"])
    except urllib.error.HTTPError as e:
        print("Http Error: " + e.msg)
        return
    return full_file_path


# url: domain for relative url resolution
# E.g.: http://my.domain.com/public/files/
def get_site_domain_urls(url=None):
    root_domain_url = None  # E.g.: http://my.domain.com/
    site_domain_url = None  # E.g.: http://my.domain.com/public/files/
    if url:
        m = re.match(r'^((http://|https://)([a-z0-9]+[a-z0-9\-\.]*[a-z0-9]+))(.*)', url, re.I)
        if m and (not m.group(4) or m.group(4).startswith("/")):
            root_domain_url = m.group(1) + "/"
            if not url.endswith("/"):
                site_domain_url = url + "/"

    if root_domain_url and site_domain_url:
        return root_domain_url, site_domain_url
    else:
        return


# file: full path to the html file
def extract_file_names(file, site_domain=None):
    site_domain_urls = get_site_domain_urls(site_domain)
    file_format = r'.*href[\s]*=[\s]*["\']((http://|https://|//|/)*.+\.pdf)["\'].*'
    results = []
    state = 0  # 0 for initial, 1 for <, 2 for <a, 3 for <other

    f = open(file, "r")
    c = f.read(1)
    while c:
        if state == 0:
            if c == '<':
                state = 1
        elif state == 1:
            if c.lower() == 'a':
                state = 2
            elif c == '>':
                state = 0
            else:
                state = 3
        elif state == 2:
            a_string = ""
            a_char = f.read(1)
            while a_char and state == 2:
                if a_char == '>':
                    state = 0
                else:
                    a_string += a_char
                a_char = f.read(1)
            if state == 0:
                m = re.match(file_format, a_string, re.I)
                if m:
                    link_part = None
                    protocol_part = str(m.group(2)).lower()
                    if protocol_part == "http://" or protocol_part == "https://":
                        link_part = m.group(1)
                    elif site_domain_urls:
                        if protocol_part == "//":
                            link_part = site_domain_urls[0] + m.group(1)[2:]
                        elif protocol_part == "/":
                            link_part = site_domain_urls[0] + m.group(1)[1:]
                        else:
                            link_part = site_domain_urls[1] + m.group(1)

                    if link_part:
                        print("Found " + link_part)
                        results.append(link_part)
        elif state == 3:
            if c == '>':
                state = 0
        c = f.read(1)

    print(site_domain)
    print("Fount " + str(len(results)) + " links.")
    return results


def main():
    site_url = "http://www.budaedu.org/ebooks/6-EN.php"
    file_dir = "C:\\Users\\Lasantha\\Downloads\\budaedu_ebooks"
    do(init, site_url, file_dir)
    index_file = do(download, site_url, file_dir)
    download_list = do(extract_file_names, index_file, "http://ftp.budaedu.org/ebooks/pdf/")
    for index, url in enumerate(download_list):
        print("[ " + str(index + 1) + " of " + str(len(download_list)) + " ]")
        download(url, file_dir, False)
    print("Done.")


__author__ = 'Lasantha'
if __name__ == "__main__":
    main()