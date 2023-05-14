from collections import namedtuple

from django import template

register = template.Library()

@register.filter
def get_hx_attr(obj, attr):
    return obj[attr]

@register.filter(name='in_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()

@register.tag
def set_query_string_param(parser, token):
    """
    Django template tag to set/unset url query string parameter
    or replace parameter's value if it's already set
    ---------
    USAGE
    {% set_query_string_param <param_1_name> <param_1_value> <param_2_name> <param_2_value> ... %}
    tag takes even number of arguments
    param names and values may be context variables or strings
    if param value is empty string or None
    or variable that contain empty string or None,
    then that param will be removed from current url query string if present
    ---------
    EXAMPLE (page_num is context variable):
    src="{% set_query_string_param 'page' page_num %}"
    RESULT (if page_num = 3):
    (if query string was ?gender=male)
    src="?gender=male&page=3"
    (if query string was ?gender=male&page=2)
    src="?gender=male&page=3"
    (if there was no query string)
    src="?page=3"
    OTHER EXAMPLES
    src="{% set_query_string_param filter_name filter_value 'page' 3 %}"
    (if filter_name = gender, filter_value = male)
    src="?gender=male&page=3"
    src="{% set_query_string_param filter_name None 'page' page_num %}"
    (if filter_name = gender, page_num = 3, query string was ?gender=male&page=2)
    src="?page=3"
    ---------
    CAUTION
    if you remove all query string parameters through the tag, then it will
    return empty string. Like this (suppouse current query str = ?gender=male)
    <a href="{% set_query_string_param gender '' %}">
        Click on me and nothing will change
    </a>
    so if you click on such link, query string will stay ?gender=male.
    in such cases use it with {% url %} tag
    <a href="{% url 'catalog:filter' %}{% set_query_string_param gender '' %}">
        Click on me and reset filtering parameters
    </a>
    or tweak the script to return '?' instead of empty string - it will solve
    the problem
    ---------
    REQUIRES to set this in settings.py:
    TEMPLATES = [{
        ...
        'OPTIONS': {
            ...
            'context_processors': [
                ...
                'django.core.context_processors.request',
                ...
            ],
            ...
        },
        ...
    }]
    """

    params = get_tag_args(token)

    return QueryStringSetValueNode(params)


def get_tag_args(token):
    arguments = token.split_contents()
    del arguments[0]  # delete tag name

    if len(arguments) < 2 or len(arguments) % 2 != 0:
        raise template.TemplateSyntaxError(
            "%r tag requires even number of argument (min 2)" % token.contents.split()[0]
        )

    TagArgsPair = namedtuple('TagArgsPair',
        ['str_repr_of_name_param', 'str_repr_of_value_param'])

    tag_args = [TagArgsPair(arguments[x], arguments[x + 1])
        for x in range(0, len(arguments), 2)]

    return tag_args


class QueryStringSetValueNode(template.Node):
    def __init__(self, tag_args):
        self.tag_args = tag_args


    def render(self, context):
        query_string_params = context.request.GET.copy()
        query_string_params_to_set = self.evaluate_query_string_params(context)

        return self.make_query_string(query_string_params, query_string_params_to_set)


    @staticmethod
    def make_query_string(query_string_params, query_string_params_to_set):
        for name, value in query_string_params_to_set.items():
            if (value == '' or value is None):
                query_string_params.pop(name, None)
            else:
                query_string_params[name] = value

        if not query_string_params:
            return ''
        return '?' + query_string_params.urlencode()


    def evaluate_query_string_params(self, context):
        return {
            self.evaluate_tag_arg(context, x.str_repr_of_name_param):
            self.evaluate_tag_arg(context, x.str_repr_of_value_param)
            for x in self.tag_args
        }


    def evaluate_tag_arg(self, context, tag_argument):
        if self.represents_string(tag_argument):
            value = tag_argument[1:-1]
        else:
            value = self.get_variable_value_from_template_context(context, tag_argument)

        return value


    @staticmethod
    def represents_string(tag_argument):
        if tag_argument[0] == tag_argument[-1] and tag_argument[0] in ('"', "'"):
            return True
        return False


    @staticmethod
    def get_variable_value_from_template_context(context, variable_name):
        var = template.Variable(variable_name)

        return var.resolve(context)
