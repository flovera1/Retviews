Please find enclosed a file containing the following datasets:

- clothes_puma.csv contains static data about products
- docs is a ReadMe
- evolutions_puma.csv contains evolution of products

Purpose of the case is (i) to identify best sellers, (ii) to build a model able to predict best sellers. 


Csv file 'clothes_puma.csv'

=> product_id : url of the clothes. Unique id
=> category : list of categories where the clothes appears on the website
=> sub_category : list of sub_categories where the clothes appears on the website
=> main_ittle : title of the clothes
=> colors : one clothes (product_id) can have multiple colors


Csv file 'evolutions_puma.csv'

=> product_id : url of the clothes. Unique id
=> color : one clothes (product_id) can have multiple colors
=> timestamp
=> type and value: type of timestamp and its value ('position': position of the clothes in the catalog of the website at timestamp, 'price': price of the clothes at timestamp, 'stock_size': volume of inventory of the clothes at timestamp, 'stock_decrease': decrease of volume of inventory between timestamp-1 and timestamp)
=> size_name : for each product_id and color we have the inventory levels at size (ex: Medium, Small, Large, etc.) granularity 




