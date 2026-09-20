def migrate(cr, version):
    """Undo the one-time backfill of is_coin_product=True onto every
    pre-existing product.template row when the column was first added.
    No coin products have been imported yet, so it is safe to reset all
    of them to False; future CSV imports / manual creation still default
    to True as intended.
    """
    cr.execute("UPDATE product_template SET is_coin_product = FALSE")
