import pandas as pd
t = pd.read_csv(r'D:\\Python\Autoru_Scraper-master\autoruSpider\autoruSpider\brands.csv', sep = ',').iloc[:,2]
for record in t[:10]:
    print(record)    
print(t)