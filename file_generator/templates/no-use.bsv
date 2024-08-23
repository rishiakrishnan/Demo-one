{% set reversed_range = range(uart, -1, -1) %}

{% for num in reversed_range %}
    uart{{num}}.interrupt{% if not loop.last %},{% endif %}
{% endfor %}