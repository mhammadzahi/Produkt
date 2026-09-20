from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ------------------------------------------------------------------
    # Favorite / priority star (used by list and kanban views)
    # ------------------------------------------------------------------
    priority = fields.Selection(
        selection=[
            ('0', 'Normal'),
            ('1', 'Favorite'),
        ],
        string="Favorite",
        default='0',
    )

    # ------------------------------------------------------------------
    # Coin visual assets
    # ------------------------------------------------------------------
    obverse_image = fields.Image(
        string="Obverse Image (Vorderseite)",
        max_width=1920,
        max_height=1920,
    )
    reverse_image = fields.Image(
        string="Reverse Image (Rückseite)",
        max_width=1920,
        max_height=1920,
    )
    wp_pic_obverse_small = fields.Char(
        string="WP Picture Obverse (small)",
        help="URL of the small obverse thumbnail used on the WordPress webshop.",
    )
    wp_pic_reverse_small = fields.Char(
        string="WP Picture Reverse (small)",
        help="URL of the small reverse thumbnail used on the WordPress webshop.",
    )

    # ------------------------------------------------------------------
    # Numismatic technical specifications
    # ------------------------------------------------------------------
    is_coin_product = fields.Boolean(
        string="Is a Numismatic Coin",
        default=True,
        index=True,
    )
    coin_metal = fields.Selection(
        selection=[
            ('gold', 'Gold (.999 / .9999)'),
            ('silver', 'Silver (.999)'),
            ('platinum', 'Platinum (.9995)'),
            ('palladium', 'Palladium'),
            ('bimetal', 'Bi-Metal / Base Metal'),
            ('other', 'Other'),
        ],
        string="Precious Metal",
        tracking=True,
    )
    coin_finish = fields.Selection(
        selection=[
            ('proof', 'Proof (PP)'),
            ('silk', 'Silk Finish'),
            ('antique', 'Antique Finish'),
            ('bu', 'Brilliant Uncirculated (BU)'),
            ('color', 'Colorized / Special Application'),
        ],
        string="Finish / Erhaltung",
        tracking=True,
    )
    coin_weight = fields.Char(
        string="Weight",
        help="e.g., 1 oz, 2 oz, 0.5 g, 31.1 g",
    )
    coin_diameter = fields.Float(
        string="Diameter (mm)",
        digits=(6, 2),
    )
    coin_mintage = fields.Integer(
        string="Mintage (Auflage)",
        tracking=True,
    )
    issuing_country_id = fields.Many2one(
        comodel_name='res.country',
        string="Issuing Authority / Land",
    )
    year_of_issue = fields.Integer(
        string="Year of Issue",
        default=lambda self: fields.Date.today().year,
    )

    kanban_dual_image_enabled = fields.Boolean(
        string="Dual Image Kanban Enabled",
        compute='_compute_kanban_dual_image_enabled',
    )

    def _compute_kanban_dual_image_enabled(self):
        enabled = self.env['ir.config_parameter'].sudo().get_param(
            'coin_product_management.enable_dual_image_kanban', 'True'
        )
        enabled = str(enabled).lower() in ('1', 'true')
        for record in self:
            record.kanban_dual_image_enabled = enabled

    @api.onchange('coin_mintage')
    def _onchange_coin_mintage_low_stock_warning(self):
        """Warn the user when the mintage is below the configured low mintage threshold."""
        threshold = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'coin_product_management.low_mintage_threshold', default=999
            )
        )
        if self.coin_mintage and 0 < self.coin_mintage <= threshold:
            return {
                'warning': {
                    'title': "Low Mintage",
                    'message': f"This coin has a low mintage ({self.coin_mintage}), "
                               f"at or below the configured alert limit of {threshold}.",
                }
            }
