from odoo import api
from odoo.api import SUPERUSER_ID
from odoo.fields import Command


def migrate(cr, version):
    """Give every existing coin product the Coin Cover variants (Capsule, Box).

    Done in two steps on purpose: adding the line with only Capsule makes Odoo
    write that value onto the product's existing variant (see
    product.template._create_variant_ids, single-value lines), so the variant
    that holds the stock becomes "Capsule" instead of being archived. Adding
    Box afterwards then creates one new variant, starting at 0 stock.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    attribute = env.ref('coin_product_management.product_attribute_coin_cover', raise_if_not_found=False)
    capsule = env.ref('coin_product_management.product_attribute_value_capsule', raise_if_not_found=False)
    box = env.ref('coin_product_management.product_attribute_value_box', raise_if_not_found=False)
    if not (attribute and capsule and box):
        return

    templates = env['product.template'].with_context(active_test=False).search([
        ('is_coin_product', '=', True),
    ]).filtered(lambda t: attribute not in t.attribute_line_ids.attribute_id)
    for template in templates:
        template.write({'attribute_line_ids': [Command.create({
            'attribute_id': attribute.id,
            'value_ids': [Command.set(capsule.ids)],
        })]})
        line = template.attribute_line_ids.filtered(lambda l: l.attribute_id == attribute)
        line.write({'value_ids': [Command.link(box.id)]})
