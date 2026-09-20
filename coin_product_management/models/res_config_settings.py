from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    coin_default_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Default Coin Currency",
        config_parameter='coin_product_management.default_currency_id',
    )
    coin_enable_dual_image_kanban = fields.Boolean(
        string="Show Obverse & Reverse in Kanban",
        config_parameter='coin_product_management.enable_dual_image_kanban',
        default=True,
    )
    coin_low_mintage_threshold = fields.Integer(
        string="Low Mintage Alert Limit",
        config_parameter='coin_product_management.low_mintage_threshold',
        default=999,
    )
