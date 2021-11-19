import csv
import scrapy
import lxml.html as lh
from bs4 import BeautifulSoup

def parse_row(tds):
    name_title= "{} {}".format(tds[0].find("a").contents[0], tds[0].find("a").contents[2])
    #title = tds[0].find("a").contents[2]
    department = tds[1].get_text()
    areas = tds[2].get_text()
    contact_cell = tds[3].contents

    contact = None
    if len(contact_cell) == 3:
        contact = '{} {}'.format(contact_cell[0], tds[3].find("a").get_text())
    else:
        contact = "{}".format(tds[3].find("a").get_text())


    return [name_title, department, areas, contact]


class BlogSpider(scrapy.Spider):
    name = "blogspider"
    start_urls = ["https://www.ualberta.ca/computing-science/faculty-and-staff/faculty"]

    def parse(self, response):
        faculty_members = []
        soup = BeautifulSoup(
            response.selector.xpath(
                '//*[@id="layoutcontainer"]/div/div[3]/div/div[2]/div/table/tbody'
            ).get(),
            "html.parser",
        )
        rows = soup.find_all("tr")

        for row in rows:
            tds = row.find_all("td")
            faculty_members.append(parse_row(tds))

        headers = ["name_title", "department", "areas", "contact"]

        faculty_members.insert(0, headers)

        with open("output.csv", "w") as output_f:
            csv_writer = csv.writer(output_f)
            csv_writer.writerows(faculty_members)

