# Webserver for Amplifier hackathon project

To run the server
```
virtualenv amplifier_env
source amplifier_env/bin/activate
pip3 install -r requirements.txt
python3 run_debug.py
```

## Want to play locally

Switch the class of the db in controller.py

from 

```python
db = PandasDB('all_partners_ranked_by_sales.csv', 'all_top_selling_products_per_partner.csv',
              'revised_category_names.csv', 'all_skeletons.csv')
```

to

```python
db = MockPandasDB('all_partners_ranked_by_sales.csv', 'all_top_selling_products_per_partner.csv',
              'revised_category_names.csv', 'all_skeletons.csv')
```

You will also need to have google cloud credentials to use the voice API :

```
export GOOGLE_APPLICATION_CREDENTIALS="/.../somewhere/..../.gcp/credentials.json"
```