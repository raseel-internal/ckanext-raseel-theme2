import six

from flask import Blueprint

import ckan.lib.helpers as h
from ckan.plugins.toolkit import _, g, request, redirect_to, url_for
from ckan.views.user import logged_out, logout, logged_out_page
from ckan.views.dashboard import index

blueprint = Blueprint(u'user_overrides', __name__)

def logout_override():
    # Do any plugin logout stuff
    for item in plugins.PluginImplementations(plugins.IAuthenticator):
        response = item.logout()
        if response:
            return response

    url = h.url_for(u'user.logged_out_page_override')
    return h.redirect_to(
        _get_repoze_handler(u'logout_handler_path') + u'?came_from=' + url,
        parse_url=True)


def logged_out_override():
    # redirect if needed
    came_from = request.params.get(u'came_from', u'')
    if h.url_is_local(came_from):
        return h.redirect_to(str(came_from))
    return h.redirect_to(u'user.logged_out_page_override')


def logged_out_page_override():
    return h.redirect_to(u'home.index')

blueprint.add_url_rule(u'/user/logged_out_redirect',view_func=logged_out_page_override)

def get_blueprints():
    return [blueprint]