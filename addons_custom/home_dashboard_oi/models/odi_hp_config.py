# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from random import randint
from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

class OdiHpConfig(models.Model):
    _name = "odi.hp.config"
    _description = "Page Config"
    _check_company_auto = True


    # Define the selection list for button styles
    BUTTON_STYLES = [
        ('btn-primary', 'Primary'),
        ('btn-secondary', 'Secondary'),
        ('btn-success', 'Success'),
        ('btn-danger', 'Danger'),
        ('btn-warning', 'Warning'),
        ('btn-info', 'Info'),
        ('btn-light', 'Light'),
        ('btn-dark', 'Dark'),
        ('btn-teal', 'Teal'),
    ]
    # Define the selection list for icons
    ICON_SET = [
        ('fa fa-bar-chart', 'Bar Chart'),
        ('fa fa-line-chart', 'Line Chart'),
        ('fa fa-pie-chart', 'Pie Chart'),
        ('fa fa-area-chart', 'Area Chart'),
        ('fa fa-bell', 'Bell'),
        ('fa fa-check', 'Check'),
        ('fa fa-cog', 'Settings'),
        ('fa fa-user', 'User'),
        ('fa fa-heart', 'Heart'),
        ('fa fa-briefcase', 'Briefcase'),
        ('fa fa-calendar', 'Calendar'),
        ('fa fa-cloud', 'Cloud'),
        ('fa fa-comments', 'Comments'),
        ('fa fa-envelope', 'Envelope'),
        ('fa fa-gear', 'Gear'),
        ('fa fa-globe', 'Globe'),
        ('fa fa-home', 'Home'),
        ('fa fa-lock', 'Lock'),
        ('fa fa-search', 'Search'),
        ('fa fa-shopping-cart', 'Shopping Cart'),
        ('fa fa-star', 'Star'),
        ('fa fa-sync', 'Sync'),
        ('fa fa-tag', 'Tag'),
        ('fa fa-trash', 'Trash'),
        ('fa fa-video-camera', 'Video Camera'),
        ('fa fa-volume-up', 'Volume Up'),
        ('fa fa-wrench', 'Wrench'),
        ('fa fa-tasks', 'Tasks'),
        ('fa fa-list', 'List'),
        ('fa fa-clipboard', 'Clipboard'),
        ('fa fa-file', 'File'),
        ('fa fa-folder', 'Folder'),
        ('fa fa-check-square', 'Check Square'),
        ('fa fa-edit', 'Edit'),
        ('fa fa-save', 'Save'),
        ('fa fa-copy', 'Copy'),
        ('fa fa-paperclip', 'Paperclip'),
        ('fa fa-share', 'Share'),
        ('fa fa-exclamation-circle', 'Warning'),
        ('fa fa-question-circle', 'Help'),
        ('fa fa-info-circle', 'Info'),
        ('fa fa-credit-card', 'Credit Card'),
        ('fa fa-sign-out', 'Sign Out'),
        ('fa fa-sign-in', 'Sign In'),
        ('fa fa-lock-open', 'Unlock'),
        ('fa fa-user-plus', 'Add User'),
        ('fa fa-user-minus', 'Remove User'),
        ('fa fa-building', 'Building'), 
    ]

    name = fields.Char(string="Name", required=True, 
        index='trigram', tracking=True)
    active = fields.Boolean( default=True,
        help="If you uncheck the active field, it will disable the record rule without deleting."
    )
    user_ids = fields.Many2many('res.users', string="Allowed Users", 
        required=True, tracking=True, index=True)
    db_code = fields.Integer(string='Sequence', index=True, 
        required=True, tracking=True, copy=False)
    db_type = fields.Selection(
        selection=[
            ('card', 'Card'), ('graph', 'Graph'), ('list', 'List'),
        ],
        string='Display Type', index=True, required=True, tracking=True, default='card'
    )  
    kpi = fields.Char(string="KPI Target",  index=True, default='0.00',
        help="Mention your budgeted/targed value here -Text Value")
    model = fields.Char(string="Model",  index=True, default='',
        help="Odoo model name: sale.order, crm.lead, account.move, hr.employee")
    field = fields.Char(string="Data Field",  index=True, default='',
        help="Field name for Sum, Text and Date")
    date_field = fields.Char(string="Date Filter",  index=True, default='',
        help="Date field in the selected model for applying filters")
    domain = fields.Text(string='Filter Domain', default='[]', 
        help="Domain filter for the model.")
    custom_psql = fields.Boolean(string='Use Custom SQL', default=False,
        help="User defined SQL query."
    )
    psql = fields.Text(string='SQL Query',
        help="Raw SQL query. Ensure it is sanitized to prevent SQL injection.",
        compute="_compute_psql", store=True, readonly=False
    )
    color = fields.Selection(
        selection=BUTTON_STYLES,
        string='Card Style', index=True, required=True, 
        tracking=True, default='btn-info'
    )
    icon = fields.Selection(
        selection=ICON_SET,
        string="Card Icon",
        required=True,
        index=True,
        default='fa fa-bar-chart'
    )
    company_id = fields.Many2one('res.company', string='Company', index=True,
        default=lambda self: self.env.company,
        help="Company related Config")
    category = fields.Selection(
        selection=[
            ('kpi', 'KPI'),('acc', 'Accounts'), ('sal', 'Sales'), ('crm', 'CRM'),
            ('prj', 'Projects'), ('mrp', 'Production'), ('inv', 'Inventory'),
            ('hr', 'HRM'),('pos', 'POS'), ('pro', 'Property'), ('fac', 'Facility'),
            ('ivt', 'Invest'), ('ser', 'Services'), ('evt', 'Events'),
        ],
        string='Category', index=True, required=True, 
        tracking=True
    )
    calc = fields.Selection(
        selection=[
            ('cnt', 'Count'), ('sum', 'Sum'),
        ],
        string='Value Type', index=True, required=True, 
        tracking=True, default='cnt'
    )
    graph_type = fields.Selection(
        selection=[
            ('pie', 'Pie'),
            ('bar', 'Bar'),
            ('line', 'Line'),
            ('doughnut', 'Doughnut'),
            ('radar', 'Radar'),
        ],
        string="Graph Type", index=True, default='pie',
        help="Choose the type of graph"
    )
    graph_colors = fields.Text(
        default="#70cac1,#659d4e,#208cc2,#4d6cb1,#584999,#8e559e,#cf3650,#f65337,#fe7139,#ffa433,#ffc25b,#f8e54b",
        string="Graph Colors", 
        help="Comma-separated list of colors for the graph"
    )
    graph_legend = fields.Selection(
        selection=[('on', 'On'), ('off', 'Off')],
        string="Show Graph Legend", index=True, default='on',
        help="Choose whether the legend is displayed or not"
    )
    list_rows = fields.Integer(string="Number of Rows in List", default=10)
    model_id = fields.Many2one(
        'ir.model', string='Odoo Model', required=True, ondelete='cascade',
        help="Select the Odoo model to fetch data from."
    )
    field_ids = fields.Many2many(
        'ir.model.fields', string="Display Fields",
        domain="[('model_id', '=', model_id)]",
        help="Select the fields to show in the graph or card."
    )
    date_field_id = fields.Many2one(
        'ir.model.fields', string="Date Field",
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['date', 'datetime'])]",
        help="Select a date field in the model for applying filters."
    )
    sum_field_id = fields.Many2one(
        'ir.model.fields', string="Amount Field",
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['integer', 'float', 'monetary'])]",
        help="Select a numeric field for sum calculations."
    )
    filter_id = fields.Many2one("ir.filters", string="Predefined Filter", 
        domain="[('model_id', '=', model)]", 
        help="Select a predefined filter to apply.")
    is_all = fields.Boolean(string="All Users", default=False)
    is_own = fields.Boolean(string="Own Document", default=False)
    uid_field_id = fields.Many2one(
        'ir.model.fields', string="User Field",
        domain="[('model_id', '=', model_id), ('relation', '=', 'res.users')]",
        help="Select a user-related field from the selected model."
    )


    @api.model_create_multi
    def create(self, vals_list):
        last_codes = {
            'card': self.search([('db_type', '=', 'card')], order='db_code desc', limit=1).db_code or 0,
            'graph': self.search([('db_type', '=', 'graph')], order='db_code desc', limit=1).db_code or 0,
            'list': self.search([('db_type', '=', 'list')], order='db_code desc', limit=1).db_code or 0,
        }
        
        card_no = last_codes['card']
        graph_no = last_codes['graph']
        list_no = last_codes['list']

        for vals in vals_list:
            if 'db_code' not in vals or not vals['db_code']:
                db_type = vals.get('db_type')
                if db_type == 'card':
                    card_no += 1
                    vals['db_code'] = card_no
                elif db_type == 'graph':
                    graph_no += 1
                    vals['db_code'] = graph_no
                elif db_type == 'list':
                    list_no += 1
                    vals['db_code'] = list_no

        return super(OdiHpConfig, self).create(vals_list)


    def write(self, vals):
        if 'db_code' in vals or 'db_type' in vals:
            for record in self:
                db_code = vals.get('db_code', record.db_code)
                db_type = vals.get('db_type', record.db_type)
                self._check_duplicate_db_code(db_code, db_type, record.id)
        return super().write(vals)

    def _check_duplicate_db_code(self, db_code, db_type, exclude_id=False):
        if db_code and db_type:
            domain = [('db_code', '=', db_code), ('db_type', '=', db_type)]
            if exclude_id:
                domain.append(('id', '!=', exclude_id))

            existing = self.search_count(domain)
            if existing:
                raise UserError(f"The sequence '{db_code}' is already assigned for type '{db_type}'. Please choose a different value.")

    @api.onchange("model_id")
    def _onchange_model_id(self):
        """
        When model_id is changed, reset all dependent fields and 
        auto-select relevant date, sum, and primary display fields.
        """
        self.field_ids = [(5, 0, 0)]  # Clear Many2many field
        self.sum_field_id = False
        self.date_field_id = False
        self.date_field = ""
        self.field = ""
        self.filter_id = False
        self.domain = "[]"
        self.custom_psql = False
        self.psql = ""

        if not self.model_id:
            return

        # Get model name
        self.model = self.model_id.model

        # Fetch all fields in the selected model
        fields = self.env["ir.model.fields"].sudo().search([("model_id", "=", self.model_id.id)])

        # Auto-select Date Field (Prioritize known date fields, fallback to 'create_date')
        date_fields = [f for f in fields if f.ttype in ["date", "datetime"]]
        date_priority = ["date", "date_order", "date_created", "date_created", "created_date", "invoice_date", "payment_date", "doc_date"]

        self.date_field_id = next((f for f in date_fields if f.name in date_priority), None)
        if not self.date_field_id:
            self.date_field_id = next((f for f in date_fields if f.name == "create_date"), None)

        # Set `date_field` based on `date_field_id`
        self.date_field = self.date_field_id.name if self.date_field_id else ""

        amount_priority = [
            "amount", "expected_revenue", "value_amount", "value", "line_amount", 
            "revenue", "revenue_amount", "invoice", "invoice_amount", 
            "total_amount", "amount_total", "total", 
            "net_amount", "gross_amount", "subtotal", "discount_amount"  # Added new fields
        ]

        # Auto-select Sum Field (Prioritize fields containing 'amount', 'total_amount', 'line_amount', etc.)
        for field in fields:
            if field.ttype in ["monetary", "float", "integer"]:
                # Check if the field name contains any of the prioritized keywords
                if any(priority_keyword in field.name for priority_keyword in amount_priority):
                    self.sum_field_id = field
                    break  # Prioritize the first match         

        # Auto-select Primary Display Fields (Take first two matching fields)
        display_priority = ["type", "category", "group", "state", "stage", "type_id", "category_id", "group_id", "cat_id", "state_id", "stage_id","user_id", "partner_id", "name"]
        selected_fields = [f for f in fields if f.name in display_priority][:2]

        if selected_fields:
            self.field_ids = [(6, 0, [f.id for f in selected_fields])]

    @api.onchange('date_field_id')
    def _onchange_date_field_id(self):
        if self.date_field_id:
            self.date_field = self.date_field_id.name
        else:
            self.date_field = ""

    @api.onchange('sum_field_id')
    def _onchange_sum_field_id(self):
        if self.sum_field_id:
            self.field = self.sum_field_id.name
            self.calc = 'sum'
        else:
            self.field = ""

    @api.onchange('filter_id')
    def _onchange_filter_id(self):
        if self.filter_id:
            self.domain = self.filter_id.domain
        else:
            self.domain = "[]"

    @api.depends("model_id", "field_ids", "sum_field_id", "filter_id", "custom_psql", "calc", "db_type", "list_rows")
    def _compute_psql(self):
        """
        Compute the SQL query dynamically based on the selected model, fields, and filter,
        but do not generate SQL if custom_psql is enabled.
        """
        for rec in self:
            if rec.custom_psql:
                continue  # Skip auto-generation if custom_psql is enabled
            
            if not rec.model_id or not rec.field_ids:
                rec.psql = ""
                rec.custom_psql = False  # Safe to modify in onchange
                continue

            # Step 1: Get Table Name and Alias
            table_name = self.env[rec.model_id.model]._table
            table_alias = "t1"  # Alias for the main table

            # Step 2: Get Selected Fields with Alias
            selected_fields = [f"{table_alias}.{field.name}" for field in rec.field_ids]

            # Step 3: Handle SUM / COUNT Operations
            if rec.calc == "sum" and rec.sum_field_id:
                selected_fields.append(f"SUM({table_alias}.{rec.sum_field_id.name}) AS total")
            elif rec.calc == "cnt":
                selected_fields.append(f"COUNT(*) AS count")

            # Step 4: Generate WHERE Clause from Domain
            where_clause = "1=1"
            if rec.filter_id:
                domain = safe_eval(rec.filter_id.domain or "[]")
                where_conditions = self._domain_to_sql(domain, table_alias)
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

            # Step 5: Generate GROUP BY Clause
            group_by = ", ".join([f"{table_alias}.{field.name}" for field in rec.field_ids if field.name != rec.sum_field_id.name]) or "1"

            # Step 6: Assemble SQL Query
            query = f"""
                SELECT {', '.join(selected_fields)}
                FROM {table_name} AS {table_alias}
                WHERE {where_clause}
                GROUP BY {group_by}
            """

            # Step 7: Add LIMIT clause if db_type is 'list'
            if rec.db_type == 'list':
                list_rows = rec.list_rows or 10  # Default to 10 if list_rows is not set
                query = query.rstrip(";")  # Remove any existing semicolon
                query += f" LIMIT {list_rows};"

            # Store generated SQL in psql field
            rec.psql = query.strip()
            
    @staticmethod
    def _domain_to_sql(domain, table_alias):
        """
        Convert Odoo domain format to SQL WHERE conditions using table alias.
        """
        sql_conditions = []
        for condition in domain:
            if isinstance(condition, (list, tuple)) and len(condition) == 3:
                field, operator, value = condition
                if operator == "=":
                    sql_conditions.append(f"{table_alias}.{field} = '{value}'")
                elif operator == "!=":
                    sql_conditions.append(f"{table_alias}.{field} != '{value}'")
                elif operator == "like":
                    sql_conditions.append(f"{table_alias}.{field} LIKE '%{value}%'")
                elif operator in (">", "<", ">=", "<="):
                    sql_conditions.append(f"{table_alias}.{field} {operator} '{value}'")
                elif operator == "in" and isinstance(value, list):
                    sql_conditions.append(f"{table_alias}.{field} IN ({', '.join(map(str, value))})")
                elif operator == "not in" and isinstance(value, list):
                    sql_conditions.append(f"{table_alias}.{field} NOT IN ({', '.join(map(str, value))})")
        return sql_conditions

   