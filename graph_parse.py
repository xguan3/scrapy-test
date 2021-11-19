import csv
import scrapy
from bs4 import BeautifulSoup
from PIL import Image
import numpy as np
#import urllib
from urllib.request import urlretrieve, urlopen
import ssl
#certificate --> ssl 是否本地的信任的证书，取消ssl验证
ssl._create_default_https_context = ssl._create_unverified_context
def parse_row(tds):
    name_title = "{} {}".format(
        tds[0].find("a").contents[0], tds[0].find("a").contents[2]
    )
    department = tds[1].get_text()
    areas = tds[2].get_text()
    contact_cell = tds[3].contents

    contact = None
    if len(contact_cell) == 3:
        contact = "{} {}".format(contact_cell[0], tds[3].find("a").get_text())
    else:
        contact = "{}".format(tds[3].find("a").get_text())

    return [name_title, department, areas, contact]


class BlogSpider(scrapy.Spider):
    name = "blogspider"
    start_urls = ["https://www.ualberta.ca/computing-science/faculty-and-staff/faculty"]
    faculty_members = []

    def parse_image(self, response):
        name = response.meta.get("name")  #meta -->dic 
        soup = BeautifulSoup(
            response.selector.xpath(
                '//*[@id="layoutcontainer"]/div/div[3]/div/div[2]/div[1]/div[1]/div[1]/img'
            ).get()
        )
        img = soup.find("img") #soup.find("img") into dictionary -->
        img_url = img["src"] #in this dictionary return img中‘src'对应的值 key value, pair
        img_output_name = "{}.jpg".format(name)
        if img_url and img_url.startswith('http') and (img_url.endswith('png') or img_url.endswith('jpg') or img_url.endswith('jpeg')):
            print(img_url)
            f = urlopen(img_url)
            # https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python
            image = Image.open(f).convert('L', (0.2989, 0.5870, 0.1140, 0))
            image.thumbnail((224, 224))
            image.save(img_output_name)

    def parse(self, response): #
        soup = BeautifulSoup(
            response.selector.xpath(
                '//*[@id="layoutcontainer"]/div/div[3]/div/div[2]/div/table/tbody'
            ).get(),    #return the content in this link
            "html.parser", #how it was written in the documentation
        )#create a beatufiulsoup instance get html string
        rows = soup.find_all("tr") #soup = BeautifulSoup(html_doc, 'html.parser') return all the elements from the webpage 
        #soup.find_all('tr') find all elements with 'tr' in them

        for row in rows: 
            tds = row.find_all("td") #for item in 'tr', find all elements with 'td'
            profile = parse_row(tds)
            self.faculty_members.append(profile)
            profile_url = tds[0].find("a", href=True)["href"]
            yield scrapy.Request(
                profile_url,
                callback=self.parse_image,
                meta={"name": tds[0].find("a").contents[0]},
            )

        headers = ["name_title", "department", "areas", "contact"]

        self.faculty_members.insert(0, headers)

        with open("output.csv", "w") as output_f:
           csv_writer = csv.writer(output_f)
           csv_writer.writerows(self.faculty_members)