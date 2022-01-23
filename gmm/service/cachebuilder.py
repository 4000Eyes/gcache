from flask import current_app
from model.extensions import NeoDB, RedisCache
import json
import neo4j.exceptions
import redis.exceptions

def load_category_cache():
    try:
        graph_driver = NeoDB.get_session()
        query = "MATCH (a:MerchCat)<-[:PART_OF]-(b:WebCat)<-[:SUB_CATEGORY_OF]-(c:WebSubCat) " \
                "  RETURN " \
                " a.merch_category_id, a.merch_category_name," \
                " b.web_category_id, b.web_category_name, " \
                " c.web_subcategory_id, c.web_subcategory_id " \
                " ORDER by a.merch_category_id, b.web_category_id, c.web_subcategory_id"

        result = graph_driver.run(query)
        dmerchcat = {}
        dwebcat = {}
        dwebsubcat = {}
        tempwebcat = None
        for record in result:
            dmerchcat[record["merch_category_id"]] = record["merch_category_name"]
            dwebcat[record["web_category_id"]] = dwebcat[record["web_category_name"]]
            if not tempwebcat:
                tempwebcat = record["web_category_id"]
            if tempwebcat != record["web_category_id"]:
                value = json.dumps(dwebsubcat)
                RedisCache.set("sc_" + record["web_category_id"], value)
                dwebsubcat.clear()
            dwebsubcat[record["web_subcategory_id"]] = record["web_subcategory_name"]
        RedisCache.set("merch_cats", json.dumps(dmerchcat))
        RedisCache.set("web_cats", json.dumps(dwebcat))
        return True
    except neo4j.exceptions.Neo4jError as e:
        return False
    except redis.exceptions.RedisError as e:
        return False
    except Exception as e:
        return False

def load_subcat_brand_cache():
    try:
        driver = NeoDB.get_session()
        temp = None
        d_brand_sc = []
        query = "MATCH (a:web_subcategory)<-[:APPLICABLE]-(b.brand) "\
                " WHERE a.country = 'US' " \
                " RETURN  DISTINCT a.web_subcategory_id, a.web_subcategory_name, b.brand_name, b.brand_id "\
                " ORDER by a.web_subcategory_id"
        result = driver.run(query)
        for record in result:
            if temp is None:
                temp = result["web_subcategory_id"]
            if temp != result["web_subcategory_id"]:
                temp = result["web_subcategory_id"]
                RedisCache.set("brand" + result["web_subcategory_id"], json.dumps(d_brand_sc))
                d_brand_sc.clear()
            d_brand_sc[result["brand_id"]] = result["brand_name"]

        return True
    except neo4j.exceptions.Neo4jError as e:
        return False
    except redis.exceptions.RedisError as e:
        return False
    except Exception as e:
        return False

def get_brands_by_subcategory(sub_category_id, output):
    output = []
    try:
        driver = RedisCache.get_driver()

        for val in sub_category_id:
            output.update(driver.get(val))
        return True
    except redis.exceptions.RedisError as e:
        return False

def reload_cache():
    return True

def get_value( key, output):
    try:
        driver = RedisCache.get_driver()
        value = driver.get(key)
        output.append(json.loads(value))
        return True
    except Exception as e:
        return False