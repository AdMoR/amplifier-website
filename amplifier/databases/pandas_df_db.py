import pandas as pd
import json


class PandasDB:
    def __init__(self, client_csv, top_selling_csv, revised_cat_csv, skeletons_csv):
        delimiter = "\t"
        self.client_df = pd.read_csv(client_csv, delimiter)
        self.top_selling_df = pd.read_csv(top_selling_csv, delimiter)
        self.revised_cat_df = pd.read_csv(revised_cat_csv, delimiter)
        self.skeletons_df = pd.read_csv(skeletons_csv, delimiter)
    def is_client_name_in(self, client_name):
        return client_name in self.client_df["partner_name"].values
    def find_product_categories_for_partner(self, name):
        #df.join(top_sell_df, lsuffix="partner_name", rsuffix="partner_name", how="inner")
        return self.top_selling_df[self.top_selling_df["partner_name"] == name]. \
            sort_values("num_sales_event", ascending=False).head()["category_name"].values
    def find_adapted_name_and_template(self, category_name):
        results = self.revised_cat_df[self.revised_cat_df["category_name"] == category_name][["revised_category_name", "compatible_brandless_skeletons"]].values
        adapted_name, template_ids = str(results[0][0]), json.loads(results[0][1])
        all_templates = self.skeletons_df[self.skeletons_df["id"].isin(template_ids)]
        templates = all_templates[all_templates["is_branded"] < 0.5]["body"].values
        return adapted_name, templates





