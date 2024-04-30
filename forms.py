from flask import request


class EntityForm:
    def __init__(self, entity):
        self.submitted = False
        self.errors = []
        self.entity = entity

    @property
    def submitted_and_valid(self):
        return self.submitted and len(self.errors) == 0

    @property
    def create_form(self):
        return self.entity.id is None

    def validate_on_submit(self):
        if request.method != 'POST':
            return False

        self.submitted = True
        self.entity.form = request.form
        self.errors = self.entity.validate()

        return len(self.errors) == 0
