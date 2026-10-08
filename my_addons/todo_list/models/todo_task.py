from odoo import models, fields

class TodoTask (models.Model):
  _name = "todo.task"
  _description = "Todo task"

  name = fields.Char('Task name', required=True)
  due_date = fields.Date('Deadline')
  done = fields.Boolean('Is Done', default=False)