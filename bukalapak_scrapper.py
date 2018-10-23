from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd

class ScraperBukalapak:
    def __init__(self, driver_path = 'chromedriver.exe', incognito_mode=True, link_pelapak=None):
        self.nama = []
        self.title = []
        self.teks = []
        if incognito_mode:
            option = webdriver.ChromeOptions()
            option.add_argument("--incognito")
            self.driver = webdriver.Chrome(driver_path, chrome_options= option)
        else:
            self.driver = webdriver.Chrome(driver_path)

        if link_pelapak != None:
            url = 'https://www.bukalapak.com/u/' + link_pelapak
            self.driver.get(url)
            self.load_semua_barang()
            self.nama_pelapak = self.get_nama_pelapak()
            self.elements, self.list_barang, self.links_barang, self.review = self.get_product_list_name()
            # self.driver.close()

    def prepare_data(self, link_pelapak):
        url = 'https://www.bukalapak.com/u/' + link_pelapak
        self.driver.get(url)
        self.load_semua_barang()
        self.nama_pelapak = self.get_nama_pelapak()
        self.elements, self.list_barang, self.links_barang, self.review = self.get_product_list_name()

    def get_nama_pelapak(self):
        nama_pelapak = self.driver.find_elements_by_xpath("//h5[@class='user__name']")
        names = [x.text for x in nama_pelapak]
        return names[0]

    def load_semua_barang(self):
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(5)
            try:
                stat = self.driver.find_elements_by_xpath("//div[@class='js-infinite-scroll-text o-box--small']")
                if stat[0].text == 'Semua barang sudah ditampilkan':
                    print('load semua barang ok.')
                    break
            except:
                pass

    def get_product_list_name(self):
        list_name = self.driver.find_elements_by_xpath("//a[@class='product__name line-clamp--2 js-tracker-product-link qa-list']")
        reviews = self.driver.find_elements_by_xpath("//a[@class='review__aggregate']")
        names = [x.text for x in list_name]
        links = [x.get_attribute('href') for x in list_name]
        element = [x for x in list_name]
        review = [x.get_attribute('href') for x in reviews]
        return element, names, links, review

    def explore_link(self, url = None):
        if url != None:
            self.driver.get(url)

    def get_reviews(self, urls=None, output_file_name=None):
        if output_file_name == None:
            output_file_name = "new_dataset.csv"
        else:
            output_file_name += '.csv'

        for url in urls:
            self.driver.get(url)
            last_id = self.driver.find_elements_by_xpath("//a[@class='c-pagination__link']")
            if last_id == []:
                nama = self.driver.find_elements_by_xpath("//a[@class='u-txt--small u-display-inline-block c-link-rd']")
                title = self.driver.find_elements_by_xpath("//a[@class='u-txt--bold u-fg--black u-txt--no-decoration']")
                teks = self.driver.find_elements_by_xpath("//p[@class='u-mrgn-bottom--2 u-txt--break-word u-fg--black qa-product-review-content']")
                n_na = len(nama)
                n_ti = len(title)
                n_te = len(teks)
                if n_na == n_ti and n_na and n_te and n_ti == n_te:
                    for i in range(len(nama)):
                        self.nama.append(nama[i].text)
                        self.teks.append(teks[i].text.replace('\n', ' '))
                        self.title.append(title[i].text)
            else:
                for i in range(int( last_id[ len(last_id)-1 ].text )):
                # for i in range(2):
                    nama = self.driver.find_elements_by_xpath("//a[@class='u-txt--small u-display-inline-block c-link-rd']")
                    title = self.driver.find_elements_by_xpath("//a[@class='u-txt--bold u-fg--black u-txt--no-decoration']")
                    teks = self.driver.find_elements_by_xpath("//p[@class='u-mrgn-bottom--2 u-txt--break-word u-fg--black qa-product-review-content']")
                    n_na = len(nama)
                    n_ti = len(title)
                    n_te = len(teks)
                    if n_na != n_ti or n_na != n_te or n_ti != n_te:
                        continue
                    for j in range(len(nama)):
                        self.nama.append(nama[j].text)
                        self.teks.append(teks[j].text.replace('\n', ' '))
                        self.title.append(title[j].text)
                    try:
                        next = self.driver.find_elements_by_xpath("//a[@rel='next']")
                        self.driver.get(next[0].get_attribute('href'))
                    except:
                        break
        d = {'nama':self.nama,'title':self.title, 'teks': self.teks}
        df = pd.DataFrame(d)
        df.to_csv(output_file_name, sep=";",index=True, encoding='utf-8', index_label='id')
        print(output_file_name, 'telah disimpan')

    def close_driver(self):
        self.driver.close()
        print("driver telah berhenti")



if __name__ == '__main__':
    seller_names = ['hengky_cong', 'gado_gadoit']
    scrapper = ScraperBukalapak()
    for pelapak in seller_names:
        scrapper.prepare_data(pelapak)
        review = scrapper.review
        scrapper.get_reviews(review, pelapak)
    scrapper.close_driver()
