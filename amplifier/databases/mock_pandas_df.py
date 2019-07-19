import pandas as pd
import json


class MockPandasDB:
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
    def is_client_name_in(self, client_name):
        return client_name in self.client_df["partner_name"].values
    def find_product_categories_for_partner(self, name):
        return self.top_selling_df[self.top_selling_df["partner_name"] == name]. \
            sort_values("num_sales_event", ascending=False).head()["category_name"].values
    def find_adapted_name_and_template(self, category_name):
        results = self.revised_cat_df[self.revised_cat_df["category_name"] == category_name][["revised_category_name", "compatible_brandless_skeletons"]].values
        adapted_name, template_ids = str(results[0][0]), json.loads(results[0][1])
        all_templates = self.skeletons_df[self.skeletons_df["id"].isin(template_ids)]
        templates = all_templates[all_templates["is_branded"] < 0.5]["body"].values
        return adapted_name, templates



