import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar
import json 

bar = IncrementalBar('Fetching Links :',max = 26)
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

out_file = open('data.json','w+' , encoding='ANSI')

link = 'https://24hr-meds.com/search.htm?q={}'

links = list()
for i in range(0,26):
    html = urllib.request.urlopen(link.format(letters[i])).read()
    soup = BeautifulSoup(html, 'html.parser')

    
    tags = soup.find_all('a', attrs={'class':'el'})
    for tag in tags :
        links.append(tag.get('href', None))
    bar.next()
bar.finish()
print('{} links recieved'.format(len(links)))

bar = IncrementalBar('Fetching Data from Links :',max = len(links))

for url in links :
    main_data = dict()
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    product_name = soup.find('div', attrs={'class':'synonyName'}).text

    table = soup.find("table", attrs={"class":"buyTable"})
    active_ingredient = soup.find('div', attrs={'class':'avBox'})
    if active_ingredient : active_ingredient = active_ingredient.text
    main_data['Name'] = product_name
    if active_ingredient :
        main_data['Active-Ingredients'] = active_ingredient[19:]
    variants = list ()


    headings = [th.get_text() for th in table.find("tr").find_all("th")]

    datasets = []
    for row in table.find_all("tr")[1:]:
        dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
        datasets.append(dataset)

    for dataset in datasets:
        
        for field in dataset:
            category = {field[0]:field[1]}
            variants.append(category)
        
    main_data['Product_variants'] = variants[1:-1]
    analogs = list()
    
    analog_div = soup.find('div', attrs={'class':'analogsList'})
    if analog_div : analog_div_children = analog_div.findChildren('span') 
    else :
        analog_div_children = False
    if analog_div_children :
        for spans in analog_div_children :
            analogs.append(spans.text) 
    
    if len(analogs)>1:main_data['analogs'] = analogs
    else : analogs.append('No analogs for this drug') ; main_data['analogs'] = analogs
    analogs.clear()

    image_div = soup.find('div', attrs={'class':'pic'})
    if image_div : img = image_div.findChildren('img')
    else : img = False
    if img : img_source = img[0]['src']
    main_data['Image-URL'] = img_source

    info = dict()
    info['product_desc'] = list()
    product_des_div = soup.find('div', id='fragment-1')
    if product_des_div : prod_child = product_des_div.findChild('div', attrs={'class':'text'})
    if prod_child : 
        paras = prod_child.findAll('p')
        for para in paras :
            info['product_desc'].append(para.text) 
    info['safety_info'] = list()
    product_des_div = soup.find('div', id='fragment-2')
    if product_des_div : prod_child = product_des_div.findChild('div', attrs={'class':'text'})
    if prod_child : 
        paras = prod_child.findAll('p')
        for para in paras :
            info['safety_info'].append(para.text)
    info['side-effects']= list()
    product_des_div = soup.find('div', id='fragment-3')
    if product_des_div : prod_child = product_des_div.findChild('div', attrs={'class':'text'})
    if prod_child : 
        paras = prod_child.findAll('p')
        for para in paras :
            info['side-effects'].append(para.text)
    main_data['Information'] = info
    json.dump(main_data,out_file)
    out_file.write('\n')
    bar.next()

bar.finish()
print('\n DONE !!')
out_file.close()



