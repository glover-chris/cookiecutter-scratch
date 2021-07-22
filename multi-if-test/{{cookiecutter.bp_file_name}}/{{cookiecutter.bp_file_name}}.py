{%- if cookiecutter.selection1 in ['yes', 'maybe'] %}
# selection1 was yes or maybe
{%- if cookiecutter.selection2 == 'no' %}
# selection2 was no
{% endif %}
{% endif %}

{% if 'yes' in cookiecutter._options|dicsort %}
# yes was selected in {{ cookiecutter._options }}
{% endif %}

