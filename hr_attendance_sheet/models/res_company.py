# Copyright 2020 Pavlov Media
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    use_attendance_sheets = fields.Boolean(default=False)
    attendance_sheet_range = fields.Selection(
        selection=[
            ("MONTHLY", "Month"),
            ("BIWEEKLY", "Bi-Week"),
            ("WEEKLY", "Week"),
            ("DAILY", "Day"),
        ],
        default="WEEKLY",
        help="The range of your Attendance Sheet.",
    )

    date_start = fields.Date(
        string="Date From", index=True, default=datetime.today().date()
    )
    date_end = fields.Date(string="Date To", readonly=True, index=True)

    def get_date_end(self, company, range=None, date_start=None):
        company = self.browse(company)
        range = range or company.attendance_sheet_range
        date_start = date_start or company.date_start

        if isinstance(date_start, str):
            date_start = datetime.strptime(date_start, "%Y-%m-%d")

        if range == "WEEKLY":
            return date_start + relativedelta(days=6)
        elif range == "BIWEEKLY":
            return date_start + relativedelta(days=13)
        else:
            return date_start + relativedelta(months=1, day=1, days=-1)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get("date_start"):
            res.write(
                {
                    "date_end": self.get_date_end(
                        self.id,
                        vals.get("attendance_sheet_range"),
                        vals.get("date_start"),
                    )
                }
            )
        return res

    def write(self, vals):
        if vals.get("date_start") or vals.get("attendance_sheet_range"):
            vals.update(
                {
                    "date_end": self.get_date_end(
                        self.id,
                        vals.get("attendance_sheet_range"),
                        vals.get("date_start"),
                    )
                }
            )
        return super().write(vals)

    attendance_week_start = fields.Selection(
        selection=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        string="Week Starting Day",
        default="0",
    )

    attendance_sheet_review_policy = fields.Selection(
        selection=[
            ("hr", "HR Manager/Officer"),
            ("employee_manager", "Employee's Manager or Attendance Admin"),
            ("hr_or_manager", "HR or Employee's Manager or Attendance Admin"),
        ],
        default="hr",
        help="How Attendance Sheets review is performed.",
    )

    auto_lunch = fields.Boolean(
        help="Applies a lunch period if duration is over the max time.",
    )

    auto_lunch_duration = fields.Float(
        string="Duration",
        help="The duration on an attendance that would trigger an auto lunch.",
    )

    auto_lunch_hours = fields.Float(
        string="Lunch Hours",
        help="Enter the lunch period that would be used for an auto lunch.",
    )
