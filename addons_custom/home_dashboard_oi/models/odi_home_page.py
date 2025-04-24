# -*- coding: utf-8 -*-
import pandas as pd
import logging
import pprint
import ast
import re

from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.http import request
from odoo.tools import float_utils
from odoo.tools import format_duration
from pytz import utc

_logger = logging.getLogger(__name__)

class OrchidHomePage(models.Model):
    _name = 'odi.home.page'
    _description = "Orchid Home"

    def _date_val(self, dtf):
        today = datetime.today()
        from_date, to_date = None, None  # Default to None

        if dtf == 'cy':  # Current Year
            from_date = today.replace(month=1, day=1)
            to_date = today
        elif dtf == 'cm':  # Current Month
            from_date = today.replace(day=1)
            to_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif dtf == 'lm':  # Last Month
            from_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            to_date = today.replace(day=1) - timedelta(days=1)
        elif dtf == 'ly':  # Last Year
            from_date = today.replace(year=today.year - 1, month=1, day=1)
            to_date = today.replace(year=today.year - 1, month=12, day=31)
        elif dtf == 'wk':  # This Week (Monday to Today)
            from_date = today - timedelta(days=today.weekday())
            to_date = today
        elif dtf == 'td':  # Today
            from_date = today
            to_date = today
        else:
            from_date = today
            to_date = today

        return from_date, to_date


    # User and Company base info
    @api.model
    def get_base_data(self, dtf):
        uid = request.session.uid
        user = self.env.user
        company = self.env.company
        return {
            'user_id': uid,
            'company_id': {
                'id': company.id,
                'name': company.name,
            },
        }

    # Home Page Setting Company wise
    @api.model
    def get_sett_data(self, dtf):
        user = self.env.user
        user_id = self.env.user.id
        company = self.env.company

        # Check for existing user setting
        user_setting = self.env['odi.user.setting'].sudo().with_context(prefetch_fields=False).sudo().search([
            ('user_id', '=', user_id),
            ('company_id', '=', company.id),
            ('key', '=', 'slicer')
        ], limit=1)

        if user_setting:
            if user_setting.val != dtf:
                # Update only if the value has changed
                user_setting.sudo().write({'val': dtf})
                self.env['odi.user.setting'].flush_model()  # Ensure immediate DB update
        else:
            # Create a new setting if it does not exist
            self.env['odi.user.setting'].sudo().create({
                'name': f"{user_id}_slicer",
                'user_id': user_id,
                'company_id': company.id,
                'key': 'slicer',
                'val': dtf,
                'active': True
            })
            self.env['odi.user.setting'].flush_model()  # Ensure immediate DB update

        settings = self.env['odi.hp.setting'].get_settings_data(user, company)
        return settings

    # KPI Card data
    @api.model
    def get_card_data(self, dtf, from_date=None, to_date=None):
        """Fetches card data for the dashboard with proper error handling."""
        
        # Compute date range if not provided
        if from_date is None or to_date is None:
            from_date, to_date = self._date_val(dtf)

        user_id = self.env.user.id
        company_id = self.env.company.id if self.env.company else False

        tile_data = {
            str(i): {
                'count': 0,
                'head': None,
                'model': '',
                'domain': [],
                'field': '',
                'calc': 'cnt',
                'view_mode': 'list,form',
                'views': [[False, 'list'], [False, 'form']],
                'target': 'current',
                'icon': 'fa fa-bar-chart'  # Default icon
            }
            for i in range(1, 101)
        }

        # Base domain
        domain = [
            ('active', '=', True),
            ('db_type', '=', 'card'),
        ]

        # Use OR to handle 'company_id' conditions.
        domain += [
            '|',  # OR
            ('company_id', '=', company_id),  # Match records where company_id equals the user's company
            ('company_id', '=', False),  # OR: Match records where company_id is False
        ]

        # Add the OR condition to match either 'is_all' True or user_ids containing the current user
        domain += [
            '|',  # OR
            ('is_all', '=', True),  # Match records where `is_all` is True
            ('user_ids', 'in', [user_id]),  # Match records where the current user is in `user_ids`
        ]

        db_configs = self.env['odi.hp.config'].sudo().search(domain)
        # _logger.info(f"get_card_data Domain {domain}")
        # _logger.info(f"get_card_data Data {db_configs}")

        # Populate tile data from configurations
        for rec in db_configs:
            tile_key = str(rec.db_code)  # Ensure db_code is treated as a string
            
            if tile_key in tile_data:
                tile_data[tile_key].update({
                    'head': rec.name,
                    'model': rec.model,
                    'field': rec.field,
                    'calc': rec.calc,
                    'kpi': rec.kpi,
                    'date_field': rec.date_field,
                    'user_field': rec.uid_field_id,
                    'icon': rec.icon,
                })
                
                # Parse domain safely
                try:
                    tile_data[tile_key]['domain'] = ast.literal_eval(rec.domain) if rec.domain else []
                except (ValueError, SyntaxError):
                    _logger.error(f"Invalid domain for {tile_key}: {rec.domain}")
                    tile_data[tile_key]['domain'] = []

        # Fetch counts or sums for each tile
        for tile_key, data in tile_data.items():
            if data['model'] and data['head'] is not None:
                try:
                    # Apply date filter if applicable
                    if from_date and to_date and data.get('date_field'):
                        date_domain = [(data['date_field'], '>=', from_date), (data['date_field'], '<=', to_date)]
                        data['domain'] = data['domain'] + date_domain

                    # Add filter for `is_own` if True
                    if data.get('is_own', True) and data.get('user_field'):
                        data['domain'].append((data['user_field'].name, '=', user_id))  # Use the dynamic field

                    # _logger.info(f"get_card_data Query Result {data['domain']}")
                    # Compute count or sum
                    model_env = self.env[data['model']].sudo()
                    if data['calc'] == 'sum' and data['field']:
                        records = model_env.sudo().search(data['domain'])
                        data['count'] = sum(getattr(record, data['field'], 0) for record in records if record[data['field']] is not False)
                    else:
                        data['count'] = model_env.sudo().search_count(data['domain'])
                except Exception as e:
                    _logger.error(f"Error fetching data for tile {tile_key}: {e}")
                    data['count'] = 0

        # Prepare the final response
        result = {}
        for tile, data in tile_data.items():
            result[f"{tile}_count"] = data['count']
            result[f"{tile}_head"] = data['head']
            result[f"{tile}_kpi"] = data.get('kpi', '')
            result[f"{tile}_model"] = data['model']
            result[f"{tile}_domain"] = data['domain']
            result[f"{tile}_view_mode"] = data['view_mode']
            result[f"{tile}_views"] = data['views']
            result[f"{tile}_target"] = data['target']
            result[f"{tile}_icon"] = data['icon']


        # _logger.info(f"Card Data Result: {result}")  # Log for debugging
        return result

    @api.model
    def get_graphs(self, dtf, from_date=None, to_date=None):
        # Calculate from_date and to_date if not provided
        if from_date is None or to_date is None:
            from_date, to_date = self._date_val(dtf)

        user_id = self.env.user.id
        company_id = self.env.company.id if self.env.company else False

        # Base domain
        domain = [
            ('active', '=', True),
            ('db_type', '=', 'graph'),
        ]

        # Use OR to handle 'company_id' conditions.
        domain += [
            '|',  # OR
            ('company_id', '=', company_id),  # Match records where company_id equals the user's company
            ('company_id', '=', False),  # OR: Match records where company_id is False
        ]

        # Add the OR condition to match either 'is_all' True or user_ids containing the current user
        domain += [
            '|',  # OR
            ('is_all', '=', True),  # Match records where `is_all` is True
            ('user_ids', 'in', [user_id]),  # Match records where the current user is in `user_ids`
        ]

        graph_configs = self.env['odi.hp.config'].sudo().search(domain, order="db_code asc")
        # _logger.info(f"get_graphs Domain {domain}")
        # _logger.info(f"get_graphs Data {graph_configs}")

        graphs_data = []
        for config in graph_configs:
            # Get the custom graph colors or use the default colors
            graph_colors = config.graph_colors.split(',') if config.graph_colors else [
                "#70cac1", "#659d4e", "#208cc2", "#4d6cb1", "#584999",
                "#8e559e", "#cf3650", "#f65337", "#fe7139", "#ffa433",
                "#ffc25b", "#f8e54b"
            ]

            query = config.psql
            try:
                # Collect filters
                filters = []

                # Add date filter on t1 table if provided
                if from_date and to_date and config.date_field:
                    from_date_formatted = from_date.strftime('%Y-%m-%d')
                    to_date_formatted = to_date.strftime('%Y-%m-%d')
                    filters.append(f"t1.{config.date_field} >= '{from_date_formatted}' AND t1.{config.date_field} <= '{to_date_formatted}'")

                # Add user filter on t1 table if applicable
                if config.is_own and config.uid_field_id:
                    filters.append(f"t1.{config.uid_field_id.name} = {user_id}")

                # Apply filters to the query
                if filters:
                    if "WHERE" in query.upper():
                        query = query.replace("WHERE", f"WHERE {' AND '.join(filters)} AND")
                    else:
                        query += f" WHERE {' AND '.join(filters)}"

                _logger.info(f"Graph Query Result {query}")

                self._cr.execute(query)
                res = self._cr.fetchall()  # Raw result from the query
                values = [row[2] for row in res]  # SUM values (third column)
                labels = [row[1] for row in res]  # Labels (second column)

                # Get graph type and colors from the config
                graph_type = config.graph_type  # ('pie', 'bar', 'line')
                graph_legend = config.graph_legend  # ('on', 'off', 'auto')
                graph_colors = config.graph_colors.split(',') if config.graph_colors else []

                graphs_data.append({
                    'values': values,
                    'labels': labels,
                    'header': config.name,
                    'graph_type': graph_type,
                    'graph_legend': graph_legend,
                    'graph_colors': graph_colors,
                })
            except Exception as e:
                _logger.error(f"Error fetching data for graph {config.name}: {e}")

        # _logger.info(f"Graph Data Result {graphs_data}")  # Log the result for debugging
        return graphs_data

    @api.model
    def get_lists(self, dtf, from_date=None, to_date=None):
        # Calculate from_date and to_date if not provided
        if from_date is None or to_date is None:
            from_date, to_date = self._date_val(dtf)

        user_id = self.env.user.id
        company_id = self.env.company.id if self.env.company else False

        # Base domain
        domain = [
            ('active', '=', True),
            ('db_type', '=', 'list'),
        ]

        # Use OR to handle 'company_id' conditions.
        domain += [
            '|',  # OR
            ('company_id', '=', company_id),  # Match records where company_id equals the user's company
            ('company_id', '=', False),  # OR: Match records where company_id is False
        ]

        # Add the OR condition to match either 'is_all' True or user_ids containing the current user
        domain += [
            '|',  # OR
            ('is_all', '=', True),  # Match records where `is_all` is True
            ('user_ids', 'in', [user_id]),  # Match records where the current user is in `user_ids`
        ]

        list_configs = self.env['odi.hp.config'].sudo().search(domain, order="db_code asc")
        # _logger.info(f"get_lists Domain {domain}")
        # _logger.info(f"get_lists Data {list_configs}")

        lists_data = []
        for config in list_configs:
            query = config.psql
            try:
                # Collect filters
                filters = []

                # Add date filter on t1 table if provided
                if from_date and to_date and config.date_field:
                    from_date_formatted = from_date.strftime('%Y-%m-%d')
                    to_date_formatted = to_date.strftime('%Y-%m-%d')
                    filters.append(f"t1.{config.date_field} >= '{from_date_formatted}' AND t1.{config.date_field} <= '{to_date_formatted}'")

                # Add user filter on t1 table if applicable
                if config.is_own and config.uid_field_id:
                    filters.append(f"t1.{config.uid_field_id.name} = {user_id}")

                # Apply filters to the query
                if filters:
                    if "WHERE" in query.upper():
                        query = query.replace("WHERE", f"WHERE {' AND '.join(filters)} AND")
                    else:
                        query += f" WHERE {' AND '.join(filters)}"

                _logger.info(f"get_lists query {query}")

                # Execute the query
                self._cr.execute(query)
                res = self._cr.fetchall()  # Raw result from the query

                # Get column names from the query result
                col_names = [desc[0] for desc in self._cr.description]

                # Extract data for the list
                list_items = []
                for row in res:
                    # Create a dictionary mapping column names to values
                    item_dict = {col_names[i]: str(value) if value is not None else "" for i, value in enumerate(row)}
                    list_items.append(item_dict)

                lists_data.append({
                    'items': list_items,
                    'header': config.name,
                    'columns': col_names,  # Add column names to the result
                })
            except Exception as e:
                _logger.error(f"Error fetching data for list {config.name}: {e}")

        # _logger.info(f"List Data Result {lists_data}")  # Log the result for debugging
        return lists_data

    