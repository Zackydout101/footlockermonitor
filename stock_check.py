import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import urllib.request as urllib

def scrape_site(url):
    s = requests.Session()
    response = urllib.urlopen(url)
    res = response.read()
    # hdrs = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
    # response = s.get(url=url, headers=hdrs, verify=True)
    soup = BeautifulSoup(res, "html.parser")
    try:
        if response.getcode()==404:
            print('Error Page Also Being Tracked!')
        else:
            script = str(soup.find_all(type='application/ld+json')[0]).replace("&quot;",'"')
            json_data = json.loads(script[script.index('{'): script.rfind('}') + 1])
            product_name = json_data["name"]
            product_image = json_data["image"][0]
            product_price = json_data['offers'][0]['price']
            # product_availability = json_data["offers"]['availability']
            product_sizes = json_data["offers"]
            sizes_available = []
            # print(soup)
            # print(sizeData)
            for size in product_sizes:
                if size["availability"] == "http://schema.org/InStock":
                    sizes_available.append(Decimal(size["sku"][-6:-3])/10)
            
            # print(sizes_available)
            if sizes_available:
                return {
                        'Title': product_name,
                        'Price': f'EUR {product_price}',
                        'Url': url,
                        'Image': product_image,
                        'Sizes':' '.join([str(elem) for elem in sizes_available]) ,
                        'Stock Status': 'In Stock'
                }

            else:
                return {
                        'Title': product_name,
                        'Url': url,
                        'Stock Status': 'OOS'
                }
    except Exception as e:
        print(e)



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
        "https://en.zalando.de/nike-sportswear-court-vintage-prem-trainers-whiteblacktotal-orange-ni112o0dw-a11.html"
        ]
    print(check_stocks(urls))
