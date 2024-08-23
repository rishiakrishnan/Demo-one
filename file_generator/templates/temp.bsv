{% for i in range(1,n) %}
    {{i}}
{% endfor %}


.........................


{% for i in range(n) %}
    {{i}}
{% endfor %}

..................


{% for i in X %}
    {{i}}
{% endfor %}

.....
//REVERSE
{% for i in my_list | reverse %}
    {{ i }}
{% endfor %}

...............

{% if X == 'yes' %}

{% else %}
// Not Implemented//
{% endif %}

..........


{% if X == 'yes' %}


{% endif %} 

.................

{% if X == 'yes' %}  {% else %}  {% endif %}


......

{% for i in range(a) %}  {% if not loop.last %},{% endif %}
{% endfor %}

.......
//REVERSE WITH COMMA
{% for i in my_list | reverse %}  
{{i}}
{% if not loop.last %},{% endif %}
{% endfor %}

..............