import json
import queue
import random
import re
import threading
import time
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import requests
from requests import adapters
from bs4 import BeautifulSoup
from threading import Lock

lock = Lock()


# def read_all_gav_info():
#     with open("./gav.txt", 'r') as f:


def extract_page_links(url):
    """
    Extracts all the links in a web page.
    :param url:
    :return:
    """

    try:
        time.sleep(0.5)
        s = requests.session()
        requests.adapters.DEFAULT_RETRIES = 5
        s.keep_alive = False  # 关闭多余连接
        page_content = s.get(url)
        soup = BeautifulSoup(page_content.text, 'html.parser')
        return soup.find_all('a', href=True)
    except Exception as e:
        print("Cannot explore this path: %s" % url)
        time.sleep(10)
        return None


def extract_pom_url(url, pom_url_queue: queue.Queue):
    """
    Extract all pom urls from a given url
    like：https://repo1.maven.org/maven2/ant/ant/1.4.1/ant-1.4.1.pom
    :param url:
    :return:
    """

    urls = extract_page_links(url)
    if urls is None:
        return

    for ur in urls:
        link = ur['href']
        # find a pom file, save the pom url in file
        if bool(re.match(r".+\.pom$", link)):
            # add queue
            pom_url_queue.put(urljoin(url, link))
        # go on find
        if link != "../" and '/' in link:
            u = urljoin(url, link)
            # time.sleep(5)
            extract_pom_url(u, pom_url_queue)


def process_pom_file(pom_url):
    """
    Extracts groupID, artifactID and version from a POM file.
    :param path:
    :return:
    """
    try:
        # modified in 2022-11-06
        time.sleep(0.5)
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        pom = s.get(pom_url)
        soup = BeautifulSoup(pom.text, 'html.parser')
    except Exception as e:
        print("Cannot explore this pom_path: %s" % pom_url)
        time.sleep(10)
        return None

    group_id = None
    artifact_id = None
    version = None

    # TODO: Fixes a case where a wrong groupID is extracted from the parent tag.
    for g in soup.find_all('groupId'):
        if g.parent.name == 'project':
            group_id = g
            break
        elif g.parent.name == 'parent':
            group_id = g

    # TODO: Fix the case where the artifactID is extracted from the parent tag.
    for a in soup.find_all('artifactId'):
        if a.parent.name == 'project':
            artifact_id = a
            break

    # TODO: Fix the case where the version is extracted from the parent tag
    #  2022-11-2 fixed by zc
    for v in soup.find_all('version'):
        if v.parent.name == 'project':
            version = v
            break
        elif v.parent.name == 'parent':
            version = v

    if group_id is not None and artifact_id is not None and version is not None:

        return {"groupId": validate_str(group_id.get_text()), "artifactId": validate_str(artifact_id.get_text()),
                "version": validate_str(version.get_text()), "url": pom_url}
    else:
        # print('group_id:', group_id, 'artifact_id:', artifact_id, 'version:', version, pom_url)
        return None


def validate_str(str):
    """
    This removes all the spaces, new line and tabs from a given string
    :param str:
    :return:
    """
    return ''.join(str.split())


def do_craw(url_queue: queue.Queue, pom_url_queue: queue.Queue):
    """
    use queue to execute craw
    """
    while url_queue:
        url = url_queue.get()
        # time.sleep(3)
        extract_pom_url(url, pom_url_queue)


def do_parse(pom_url_queue: queue.Queue, f1):
    """
     use queue to execute parse
    """
    while pom_url_queue:
        pom_url = pom_url_queue.get()
        # time.sleep(3)
        gav = process_pom_file(pom_url)
        if gav:
            with lock:
                f1.write(json.dumps(gav) + '\n')
        else:
            with open('./no-gav.txt', 'a', encoding='utf-8') as f:
                f.write(pom_url + '\n')
            # print(pom_url)


if __name__ == '__main__':
    base_url = r'https://repo1.maven.org/maven2/'

    url_queue = queue.Queue()
    pom_url_queue = queue.Queue()

    # 创建起始队列，将https://repo1.maven.org/maven2/ 下的所有url加入到url_queue
    for url in extract_page_links(base_url):
        link = url['href']
        if link != "../" and '/' in link:
            url_queue.put(urljoin(base_url, link))

    # open 100 thread to craw
    for idx in range(10):
        t = threading.Thread(target=do_craw, args=(url_queue, pom_url_queue))
        t.start()

    # open 100 thread to parse
    f1 = open("./gav.txt", 'w', encoding='utf-8')
    for idx in range(10):
        t = threading.Thread(target=do_parse, args=(pom_url_queue, f1))
        t.start()
