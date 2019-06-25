import sys

from amplifier.databases.sqlite3 import SQLiteDB


if __name__ == "__main__":
    csv_path = sys.argv[1]
    db = SQLiteDB("./example.db")

    if len(sys.argv) > 2:
        delimiter = sys.argv[2]
    else:
        delimiter = ";"

    with open(csv_path, "r") as f:
        for line in f:
            tokens = line.strip().split(delimiter)
            product_cat, adapted_product_cat, template_str = tokens[0:3]
            db.add_template(product_cat, adapted_product_cat, template_str, -1)
            print("ok")
