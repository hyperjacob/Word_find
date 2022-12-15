# конвертирует список с p[(5,),(8,),...] к [5,8,...]
def _convert(list_convert):

    return [itm[0] for itm in list_convert]

def total_cost(all_quantity, all_price):
    ord_ttl_cst = 0

    for i, itm in enumerate(all_price):
        ord_ttl_cst +=all_quantity[i]*all_price[i]

    return ord_ttl_cst

def total_quantity(all_quantity):
    prd_ttl_qty = 0

    for itm in all_quantity:
        prd_ttl_qty += itm
    return prd_ttl_qty


def get_total_cost(BD):
    all_product_id = BD.select_all_product_id()
    all_price = [BD.select_single_product_price(itm) for itm in all_product_id]
    all_quantity = [BD.select_single_product_quantity(itm) for itm in all_product_id]
    return total_cost(all_quantity, all_price)

def get_total_quantity(BD):
    all_product_id = BD.select_all_product_id()
    all_quantity = [BD.select_single_product_quantity(itm) for itm in all_product_id]
    return total_quantity(all_quantity)
