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
    if not get_site_domain_urls(site_url):
        print("Invalid url " + site_url)
        return False
    if not os.path.exists(file_dir):
        print("Invalid file directory " + file_dir)
        return False
    return True


def get_page_name(page_url, file_dir):
    file_name = page_url.split("/")[-1]
    if not file_name:
        file_name = "index.html"
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
        urllib.request.urlretrieve(page_url, full_file_path)
    except urllib.error.HTTPError as e:
        print("Http Error: " + e.msg)
        return
    return full_file_path


# url: domain for relative url resolution
# E.g.: http://my.domain.com/public/files/index.html
# this wll return a tuple (domain url, sub path)
def get_site_domain_urls(url=None):
    # E.g.:
    # for url =  http://my.domain.com/public/files/
    # root_domain = http://my.domain.com/
    #  relative_path = public/files/
    root_domain = None
    relative_path = None
    if url:
        m = re.match(r'^((http://|https://)([a-z0-9]+[a-z0-9\-\.]*[a-z0-9]+))(.*)', url, re.I)
        if m:
            root_domain = m.group(1)
            relative_path = str(m.group(4))

            if relative_path and not relative_path.startswith("/"):
                print("Invalid relative path in site domain: ", url)
                return None
            relative_path = relative_path[1:]

            last_sep_idx = relative_path.rfind("/") + 1
            if last_sep_idx == 0:
                relative_path = ""
            elif 0 < last_sep_idx < len(relative_path):
                relative_path = relative_path[0:last_sep_idx]

            if not root_domain.endswith("/"):
                root_domain += "/"

    if root_domain:
        return root_domain, relative_path
    else:
        print("Invalid site domain: ", url)
        return None


# file: full path to the html file
# extension: extension for the file type to download (e.g.: "pdf")
def extract_file_names(file, extension, site_domain=None):
    if not extension:
        print("No file extension provided")
        return None

    site_domain_urls = get_site_domain_urls(site_domain)

    file_format = r'.*href[\s]*=[\s]*["\']((http://|https://|//|/)*[^\s"\']+\.' + extension + ')["\'].*'
    results = []
    state = 0  # 0 for initial, 1 for <, 2 for <a, 3 for <other

    a_string = ""
    retry_counter = 0
    while retry_counter < 2:
        if retry_counter == 0:
            f = open(file, mode="r", encoding="utf8")
        else:
            f = open(file, mode="r")

        try:
            c = f.read(1)
            while c:
                if state == 0:
                    # initial state
                    if c == '<':
                        state = 1
                elif state == 1:
                    # found a tag
                    if c.lower() == 'a':
                        state = 2
                    elif c == '>':
                        state = 0
                    else:
                        state = 3
                elif state == 2:
                    # found a link
                    if c == '>':
                        state = 0
                    else:
                        a_string += c

                    if state == 0:
                        # found the closing tag of a link
                        m = re.match(file_format, a_string, re.I)
                        if m:
                            # found a valid href
                            link_part = None
                            protocol_part = str(m.group(2)).lower()
                            if protocol_part == "http://" or protocol_part == "https://":
                                link_part = m.group(1)
                            elif site_domain_urls:
                                if protocol_part == "//" or protocol_part == "./":
                                    link_part = site_domain_urls[0] + m.group(1)[2:]  # append root domain
                                elif protocol_part == "/":
                                    link_part = site_domain_urls[0] + m.group(1)[1:]  # append root domain
                                else:
                                    link_part = site_domain_urls[0] + site_domain_urls[1] + m.group(
                                        1)  # append full path

                            if link_part:
                                print("Found " + link_part)
                                results.append(link_part)
                        a_string = ""  # reset link text buffer
                elif state == 3:
                    # found a tag other than a link
                    if c == '>':
                        state = 0
                c = f.read(1)

            break  # break retry loop
        except UnicodeDecodeError as ue:
            print("Error while opening file, retrying: " + str(ue))
            f.close()
            retry_counter += 1
        except:
            f.close()
            raise

    print("Fount " + str(len(results)) + " links.")
    return results


def main(site_url, file_dir, extension):
    do(init, site_url, file_dir)
    index_file = do(download, site_url, file_dir)
    download_list = do(extract_file_names, index_file, extension, site_url)
    for index, url in enumerate(download_list):
        print("[ " + str(index + 1) + " of " + str(len(download_list)) + " ]")
        download(url, file_dir, False)
    print("Done.")


__author__ = 'Lasantha'
if __name__ == "__main__":
    # "[a-z0-9]+" for eny extension
    main("http://www.budaedu.org/ebooks/6-SR.php", "C:\\Users\\Lasantha\\Downloads\\budaedu_ebooks", "pdf")
