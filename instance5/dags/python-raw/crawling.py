import os
import json
import requests
import time
import logging
import sys
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
from typing import Dict
# import traceback


class Crawling:
    def __init__(self, data_path=os.getcwd(), site_name=""):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }
        self.driver = webdriver.Chrome  # webdriver.Safari if sys.platform.lower() == "darwin" else webdriver.Chrome
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        self.data_path = data_path
        self.site_name = site_name

        self.info_key2name = {
            "경력": "career",
            "학력": "academic_background",
            "마감일": "deadline",
            "근무지역": "location"
        }

        self.filenames = {
            "url_list": os.path.join(self.data_path, f"{self.site_name}.url_list.json"),
            "content_info": os.path.join(self.data_path, f"{self.site_name}.content_info.json"),
            "result": os.path.join(self.data_path, f"{self.site_name}.result.jsonl")
        }

    def requests_get(self, url: str) -> requests.Response:
        """
        Execute request.get for url
        :param url: url to get requests
        :return: response for url
        """
        with requests.Session() as s:
            response = s.get(url, headers=self.headers)
        return response

    def run(self):
        """
        Run all process of crawling and extract data
        """
        pass

    def scroll_down_page(self, driver):
        """
        Extract full-page source if additional pages appear when scrolling down
        :return page_source: extracted page source
        """
        page_source = ""
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            if page_source == driver.page_source:
                break
            else:
                page_source = driver.page_source

        return page_source


class CrawlingJumpit(Crawling):
    """
    Crawling of "https://www.jumpit.co.kr"
    """

    def __init__(self, data_path=os.getcwd(), site_name="jumpit"):
        super().__init__(data_path=data_path, site_name=site_name)
        self.endpoint = "https://www.jumpit.co.kr"
        self.job_category_id2name = {
            1: "서버/백엔드 개발자",
            2: "프론트엔드 개발자",
            3: "웹 풀스택 개발자",
            4: "안드로이드 개발자",
            5: "게임 클라이언트 개발자",
            6: "게임 서버 개발자",
            7: "DBA",
            8: "인공지능/머신러닝",
            9: "DevOps/시스템 엔지니어",
            10: "정보보안 담당자",
            11: "QA 엔지니어",
            12: "개발 PM",
            13: "HW/임베디드",
            15: "SW/솔루션",
            16: "IOS 개발자",
            17: "웹퍼블리셔",
            18: "크로스플랫폼 앱개발자",
            19: "빅데이터 엔지니어",
            20: "VR/AR/3D",
            22: "블록체인",
            21: "기술지원"
        }

    def get_url_list(self):
        filename = self.filenames["url_list"]
        driver = self.driver()

        job_dict = {}
        if os.path.exists(filename):
            with open(filename) as f:
                job_dict = json.load(f)

        for job_category in range(1, 23):
            if job_category in job_dict:
                continue

            driver.get(f"{self.endpoint}/positions?jobCategory={job_category}")
            time.sleep(1)

            page_source = self.scroll_down_page(driver)

            soup = BeautifulSoup(page_source, 'html')
            position_list = [
                a_tag["href"] for a_tag in soup.find_all("a") if a_tag.get("href", "").startswith("/position/")
            ]

            job_dict[job_category] = {
                "page_source": page_source,
                "position_list": position_list
            }

            with open(filename, "w") as f:
                json.dump(job_dict, f)

        driver.close()

        return job_dict

    def get_recruit_content_info(self, job_dict=None):
        if job_dict is None:
            if os.path.exists(self.filenames["url_list"]):
                with open(self.filenames["url_list"]) as f:
                    job_dict = json.load(f)
            else:
                job_dict = {}

        filename = self.filenames["content_info"]
        driver = self.driver()

        position_content_dict = {}
        if os.path.exists(filename):
            with open(filename) as f:
                position_content_dict = json.load(f)

        for job_category, job_info in job_dict.items():
            if job_category in position_content_dict:
                continue

            content_dict = {}
            for position_url in job_info["position_list"]:
                driver.get(f"{self.endpoint}{position_url}")
                time.sleep(0.1)
                content_dict[position_url] = self.driver.page_source

            position_content_dict[job_category] = content_dict

            with open(filename, "w") as f:
                json.dump(position_content_dict, f)

        driver.close()

        return position_content_dict

    def postprocess(self, position_content_dict=None):
        if position_content_dict is None:
            if os.path.exists(self.filenames["content_info"]):
                with open(self.filenames["content_info"]) as f:
                    position_content_dict = json.load(f)
            else:
                position_content_dict = self.get_recruit_content_info()

        file = open(self.filenames["result"], "w")

        postprocess_dict = {}
        if os.path.exists(self.filenames["content_info"]):
            with open(self.filenames["content_info"]) as f:
                postprocess_dict = json.load(f)

        for job_category, info_dict in position_content_dict.items():
            if job_category not in self.job_category_id2name:
                continue

            for url, content in info_dict.items():
                soup = BeautifulSoup(content, 'html')
                title = soup.find("h1").text

                try:
                    company = soup.find("div", class_="position_title_box_desc").find("a")
                except:
                    company = None
                    for a in soup.find_all(""):
                        if a.get("href", "").startswith("/company"):
                            company = a
                            break

                if not company:
                    continue

                company_name = company.text
                company_id = company.get("href")

                tag_info = {}
                position_tags = soup.find("ul", class_="position_tags")
                if position_tags:
                    for li in position_tags.find_all("li"):
                        tag_id = li.find("a").get("href")
                        tag_text = li.text
                        tag_info[tag_id] = tag_text

                tech_list = []
                position_info = soup.find("section", class_="position_info")
                if position_info:
                    for dl in position_info.find_all("dl"):
                        if dl.find("dt").text == '기술스택':
                            break
                    for div in dl.find("dd").find_all("div"):
                        tech_list.append(div.text)

                extra_info = {}
                for dl in soup.find_all('dl'):
                    key = dl.find("dt").text
                    if key in self.info_key2name:
                        value = dl.find("dd").text
                        if key == "마감일" and value == "상시":
                            value = ""
                        extra_info[self.info_key2name[key]] = value

                result = {
                    "url": f"{self.endpoint}{url}",
                    "job_category": job_category,
                    "job_name": self.job_category_id2name[job_category],
                    "title": title,
                    "company_name": company_name,
                    "company_id": company_id,
                    "tag_id": list(tag_info.keys()),
                    "tag_name": list(tag_info.values()),
                    "tech_list": tech_list
                }
                result.update(extra_info)
                postprocess_dict[url] = result
                file.write(json.dumps(result) + "\n")

        file.close()

        return postprocess_dict

    def run(self):
        job_dict = self.get_url_list()
        position_content_dict = self.get_recruit_content_info(job_dict)
        result_dict = self.postprocess(position_content_dict)
        return result_dict

def main(args):
    logger = logging.getLogger()
    logger.setLevel(
        logging.DEBUG if args.log_type.lower() == "debug" else logging.INFO
    )

    logging.info("[INFO] Set instance of crawling")
    crawling = CRAWLING_CLASS.get(args.site_type.lower(), Crawling)(data_path=args.data_path)

    logging.info("[INFO] Get recruit content info")
    if args.method == "all":
        crawling.run()
    else:
        method = getattr(crawling, args.method, None)
        if method:
            method()

CRAWLING_CLASS = {
    "jumpit": CrawlingJumpit,
}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--site_type", help="type of site", default="jobplanet")
    parser.add_argument("-l", "--log_type", help="type of log", default="info")
    parser.add_argument("-d", "--data_path", help="path of data", default=os.path.join(os.getcwd(), "data"))
    parser.add_argument("-m", "--method", help="method to execute", default="all")

    args = parser.parse_args()
    main(args)
