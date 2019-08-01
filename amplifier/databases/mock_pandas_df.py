import pandas as pd
import json
from .pandas_df_db import PandasDB

class MockPandasDB(PandasDB):
    def __init__(self, *args, **kwargs):
        self.client_df = pd.DataFrame([{"partner_name": "aaa"}])
        self.top_selling_df = pd.DataFrame([{"partner_name": "aaa", "category_name": "object", "num_sales_event": 1}])
        self.revised_cat_df = pd.DataFrame([{"partner_name": "aaa", "category_name": "object",
                                             "revised_category_name": "nice_object", "compatible_brandless_skeletons": "[1, 2]"}])
        self.skeletons_df = pd.DataFrame([{"id": 1, "is_branded": 0,
                                           "body": "Thinking about getting {PRODUCT_CATEGORY}? Select the best quality, go to {CLIENT_NAME}, {CLIENT_WEBSITE}."},
                                          {"id": 2, "is_branded": 0,
                                           "body": "Thinking about getting {PRODUCT_CATEGORY}? Select the best quality, go to {CLIENT_NAME}, {CLIENT_WEBSITE}."}
                                          ])
