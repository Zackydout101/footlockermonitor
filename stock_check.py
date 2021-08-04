import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import urllib


def scrape_site(url):

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib.request.Request(url=url, headers=hdr)
    response = urllib.request.urlopen(req).read()

    soup = BeautifulSoup(response, "html.parser")
    error_page = soup.find("h1").text.strip()

    if "404!" in error_page:
        print('Error Page Also Being Tracked!')
    else:
        script = str(soup.find_all(type = 'application/ld+json')[1])
        json_data = json.loads(script[script.index('{'): script.rfind('}') + 1])
        product_name = json_data["name"]
        product_image = json_data["image"]
        product_price = json_data["offers"][0]['priceSpecification']['price']
        product_availability = json_data["offers"][0]['availability']
        product_sizes = []
        sizeData = soup.find('ul',{'class':'variable-items-wrapper'})
        for sizes in sizeData.find_all('li'):
            product_sizes.append(sizes.text)

        if product_sizes: 
            return {
                'Title': product_name,
                'Price': f'Rs {product_price}',
                'Url': url,
                'Image': product_image,
                'Sizes':' '.join([str(elem) for elem in product_sizes]) ,
                'Stock Status': 'In Stock' if 'InStock' in product_availability else 'Out of Stock'
            }

        else:
            return {
                'Title': product_name,
                'Url': url,
                'Stock Status': 'OOS'
            }


def check_stocks(urls):
    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape_site, urls)
        
        INSTOCK = []
        for result in results:   
            if result and result not in INSTOCK:
                INSTOCK.append(result)

        return INSTOCK


if __name__ == '__main__':
    urls = [
        'https://superkicks.in/product/cl-legacy-chalk-blue-2/'
        ]
    print(check_stocks(urls))
