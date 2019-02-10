from django import forms
from django.utils.safestring import mark_safe

class RadioSelectWidget(forms.RadioSelect):
    def __init__(self, choices=None, attrs={}):
        super()
        self.choices = choices
        self.attrs = attrs

    def render(self, name, value, attrs=None, renderer=None):
        super().render(name, value, attrs)
        html = ''
        for idx, choice in enumerate(self.choices):
            input_id = attrs['id'] + '_' + str(idx)
            html += '''
<div>
<input type="radio" name="{}" value="{}" class="{}" required="" id="{}" {}>
<label class="form-check-label" for="{}">{}</label>
</div>
            '''.format(
                name,
                choice[0],
                attrs['class'],
                input_id,
                ('checked=""' if choice[0] == value else '') + (' disabled' if choice[0] == 'CANCEL' else ''),
                input_id,
                choice[1]
            )

        return mark_safe(html)
