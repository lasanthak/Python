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
        #print(httpResult[1]["Content-Length"])
    except urllib.error.HTTPError as e:
        print("Http Error: " + e.msg)
        return
    return full_file_path


def extract_file_names(file):
    results = []
    file_format = r'href=["\']((http|https)://.+\.pdf)["\'].*$'
    f = open(file, "r")
    c = f.read(1)
    state = 0  # 0 init, 1 <, 2 <a, 3 <other
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
                    print("Found: " + m.group(1))
                    results.append(m.group(1))
        elif state == 3:
            if c == '>':
                state = 0
        c = f.read(1)
    return results


def main():
    site_url = "http://www.budaedu.org/ebooks/6-SR.php"
    file_dir = "C:\\Users\\Lasantha\\Downloads\\budaedu_ebooks"
    do(init, site_url, file_dir)
    index_file = do(download, site_url, file_dir)
    download_list = do(extract_file_names, index_file)
    for index, url in enumerate(download_list):
        print("[ " + str(index + 1) + " of " + str(len(download_list)) + " ]")
        download(url, file_dir, False)
    print("Done.")


__author__ = 'Lasantha'
if __name__ == "__main__":
    main()