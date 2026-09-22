def migrate(cr, version):
    """Coin products imported before is_storable defaulted to True never got
    inventory tracking enabled, so qty_available always read 0 regardless of
    any imported quantity. Turn tracking on for existing coin products; it
    does not by itself create the missing stock quants (that still needs a
    fresh import or a manual inventory adjustment), but it stops the
    quantity display from being silently ignored.
    """
    cr.execute("UPDATE product_template SET is_storable = TRUE WHERE is_coin_product = TRUE")
