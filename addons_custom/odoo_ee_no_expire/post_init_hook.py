
def update_database_expire(env):
    env["ir.config_parameter"].sudo().set_param(
        "database.expiration_date", "2090-12-31 23:59:59"
    )

