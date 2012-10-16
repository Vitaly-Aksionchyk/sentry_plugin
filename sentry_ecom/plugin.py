import sentry_ecom
from django.core.urlresolvers import reverse

from sentry.models import Group, Event
from sentry.plugins import Plugin
from sentry.plugins.bases.tag import TagPlugin


def _get_dict_value(d, *path):
    """
    Return value by path in dict tree.

        >>> _get_dict_value({'a': {'b': {'c': 1}}}, 'a', 'b', 'c')
        1
    """
    for key in path:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return None
    return d



class EcomPlugin(Plugin):
    slug = 'ecom'
    title = 'Ecom Plugin'
    author = 'Ahalife'
    description = 'Manipulates checkout logging'
    version = sentry_ecom.VERSION

    def actions(self, request, group, action_list, **kwargs):
        action_list.append(
            ['Show events', reverse('sentry-events', kwargs={'project_id': group.project_id})]
        )
        return action_list

    def tags(self, request, group_or_event, tag_list, **kwargs):
        _f = lambda d: d.strftime('%Y/%m/%d %H:%M:%S.%f')
        if isinstance(group_or_event, Group):
            tag_list.append(_f(group_or_event.event_set.order_by('-datetime')[0].datetime))
        elif isinstance(group_or_event, Event):
            tag_list.append(_f(group_or_event.datetime))
        return tag_list


class ProfileEmailTag(TagPlugin):
    slug = 'profile-email'
    title = 'Profile Email'
    author = 'Ahalife'
    tag = 'profile_email'
    tag_label = 'Profile Email'
    version = sentry_ecom.VERSION

    def get_tag_values(self, event):
        email = _get_dict_value(event.data, 'extra', 'profile', 'email')
        if email:
            return [email]
        return  []

    def tags(self, request, group_or_event, tag_list, **kwargs):
        if not request.GET.get(self.tag):
            if isinstance(group_or_event, Group):
                emails = group_or_event.messagefiltervalue_set.filter(key=self.tag).order_by('-last_seen').values_list('value', flat=True)
                emails_list = list(emails[:3])
                count = emails.count()
                if count > 3:
                    emails_list.append('others (%s)' % (count - 3))
                tag_list.append(', '.join(emails))
            elif isinstance(group_or_event, Event):
                tag_list.extend(self.get_tag_values(group_or_event))
        return tag_list

    
class RequestMethod(TagPlugin):
    slug = 'request-method'
    title = 'Request Method'
    author = 'Ahalife'
    tag = 'request_method'
    tag_label = 'Request Method'
    version = sentry_ecom.VERSION

    def get_tag_values(self, event):
        method = _get_dict_value(event.data, 'sentry.interfaces.Http', 'method')
        if method:
            return [method]
        return  []

    def tags(self, request, group_or_event, tag_list, **kwargs):
        if not request.GET.get(self.tag):
            if isinstance(group_or_event, Group):
                tag_list.extend(group_or_event.messagefiltervalue_set.filter(key=self.tag).order_by('-last_seen').values_list('value', flat=True))
            elif isinstance(group_or_event, Event):
                tag_list.extend(self.get_tag_values(group_or_event))
        return tag_list


class EcomTaggedFuncs(TagPlugin):
    slug = 'ecom-func'
    title = 'Ecom Func name'
    author = 'Ahalife'
    tag = 'ecom_func_name'
    tag_label = 'Ecom Func name'
    version = sentry_ecom.VERSION

    TARGET_FUNCS = ('cart_add', 'checkout_cart', 'checkout', 'confirm', 'receipt')

    def get_tag_values(self, event):
        func_name = _get_dict_value(event.data, 'extra', 'funcName')
        if func_name and func_name in self.TARGET_FUNCS:
            return [func_name]
        return  []