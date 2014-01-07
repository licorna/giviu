from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()

@register.filter
@stringfilter
def clp(price):
    price = price.strip()

    def insert_thousand_separator(s, separator='.'):
        i = len(s)
        j = 0
        while i > 0:
            if j == 3:
                s = s[:i] + separator + s[i:]
                j = 0
            i -= 1
            j += 1
        return s

    # TODO: Code doesn't work, need to try on Linux, as
    # locale module is only emulated on Darwin
    #locale.setlocale( locale.LC_MONETARY, 'es_CL' )
    #return '$ ' + locale.currency(price, grouping=True)
    return '$ ' + insert_thousand_separator(price)
