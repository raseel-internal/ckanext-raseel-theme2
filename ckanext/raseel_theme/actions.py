from logging import getLogger
import os
import requests
import uuid
import zipfile

from ckan.controllers.admin import get_sysadmins
from ckan.lib.mailer import MailerException
from ckan.logic.action.create import package_create as core_package_create
from ckan.logic.action.update import package_update as core_package_update
from ckan.logic.action.get import activity_detail_list as core_activity_detail_list
from ckan.logic.action.get import dashboard_activity_list as core_dashboard_activity_list
from ckan.logic.action.get import group_activity_list as core_group_activity_list
from ckan.logic.action.get import package_activity_list as core_package_activity_list
from ckan.logic.action.get import package_show as core_package_show
from ckan.logic.action.get import recently_changed_packages_activity_list as core_recently_changed_packages_activity_list
from ckan.plugins import toolkit

from ckanext.raseel_theme import helpers
from ckanext.raseel_theme.mailer import mail_package_publish_request_to_admins


SUPPORTED_RESOURCE_MIMETYPES = [
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/x-msdownload',
    'application/msword',
    'application/vnd.google-earth.kml+xml',
    'application/vnd.ms-excel',
    'application/msexcel',
    'application/x-msexcel',
    'application/x-ms-excel',
    'application/x-excel',
    'application/x-dos_ms_excel',
    'application/xls',
    'application/x-xls',
    'wcs',
    'application/x-javascript',
    'application/x-msaccess',
    'application/netcdf',
    'text/tab-separated-values',
    'text/x-perl',
    'application/vnd.google-earth.kmz+xml',
    'application/vnd.google-earth.kmz',
    'application/owl+xml',
    'application/x-n3',
    'application/zip',
    'application/gzip',
    'application/x-gzip',
    'application/x-qgis',
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.oasis.opendocument.text',
    'application/json',
    'image/x-ms-bmp',
    'application/rar',
    'image/tiff',
    'application/vnd.oasis.opendocument.database',
    'text/plain',
    'application/x-director',
    'application/vnd.oasis.opendocument.formula',
    'application/vnd.oasis.opendocument.graphics',
    'application/xml',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/octet-stream',
    'application/xslt+xml',
    'image/svg+xml',
    'application/vnd.ms-powerpoint',
    'application/vnd.oasis.opendocument.presentation',
    'image/jpeg',
    'application/sparql-results+xml',
    'image/gif',
    'application/rdf+xml',
    'application/pdf',
    'text/csv',
    'application/vnd.oasis.opendocument.chart',
    'application/atom+xml',
    'application/x-tar',
    'image/png',
    'application/rss+xml',
    'application/geo+json'
]

log = getLogger(__name__)


@toolkit.side_effect_free
def prepare_zip_resources(context, data_dict):
    """Creates zip archive and stores it under CKAN's storage path.

    :param resources: a list of ids of the resources
    :type resources: list

    :return: a dictionary containing the zip_id of the created archive
    :rtype: dict
    """
    file_name = uuid.uuid4().hex + '.{ext}'.format(ext='zip')
    file_path = helpers.get_storage_path_for('temp-ed') + '/' + file_name
    resourceArchived = False
    package_id = None

    try:
        resource_ids = data_dict.get('resources')
        with zipfile.ZipFile(file_path, 'w') as zip:
            for resource_id in resource_ids:
                data_dict = {'id': resource_id}
                resource = toolkit.get_action('resource_show')({}, data_dict)

                url = resource.get('url')
                if resource['url_type'] == 'upload':
                    name = url.split('/')[-1]
                else:
                    name = resource['name']
                    if os.path.splitext(name)[-1] == '':
                        _format = resource['format']
                        if _format:
                            name += '.{ext}'.format(ext=_format.lower())

                if package_id is None:
                    package_id = resource['package_id']

                headers = {'Authorization': get_sysadmins()[0].apikey}
                try:
                    r = requests.get(url, headers=headers)
                except Exception:
                    continue

                content_type = r.headers['Content-Type'].split(';')[0]

                if content_type in SUPPORTED_RESOURCE_MIMETYPES:
                    resourceArchived = True
                    zip.writestr(name, r.content)
    except Exception, ex:
        log.error('An error occured while preparing zip archive. Error: %s' % ex)
        raise

    zip_id = file_name
    try:
        package = toolkit.get_action('package_show')({}, {'id': package_id})
        package_name = package['name']

        zip_id += '::{name}'.format(name=package_name)
    except:
        pass

    if resourceArchived:
        return {'zip_id': zip_id}

    os.remove(file_path)

    return {'zip_id': None}


@toolkit.side_effect_free
def package_show(context, data_dict):
    '''Override core ckan package_show.
    '''
    package = core_package_show(context, data_dict)
    # User with less perms then creator should not be able to access pending dataset
    approval_pending = package.get('approval_state') == 'approval_pending'
    try:
        toolkit.check_access('package_update', context, data_dict)
        can_edit = True
    except toolkit.NotAuthorized:
        can_edit = False
    if not can_edit and approval_pending:
        raise toolkit.ObjectNotFound
    return package


@toolkit.side_effect_free
def package_create(context, data_dict):
    '''Override core ckan package_create
    '''
    # because scheming is not working with tags vocabulary and
    # we have a list of predefined tags that should appear in the tags list
    # we are using a different field in scheming and here we need to
    # convert it to tags format and save it as tags in the database.
    #data_dict['tags'] = convert_to_tags_format(data_dict['tags_predefined'])
    dataset_dict = core_package_create(context, data_dict)

    return dataset_dict

def convert_to_tags_format(predefined_data):
    '''
        Returns list of tags in tags_format
        :param: list of predefined tags

        :returns: list of tags in tags_format
        :rtype: list
    '''
    tags_format = []

    for data in predefined_data:
        if data not in tags_format:
            tags_tmp = {}
            tags_tmp['name'] = data
            tags_tmp['state'] = 'active'
            tags_format.append(tags_tmp)

    return tags_format

@toolkit.side_effect_free
def package_update(context, data_dict):
    # because scheming is not working with tags vocabulary and
    # we have a list of predefined tags that should appear in the tags list
    # we are using a different field in scheming and here we need to
    # convert it to tags format and save it as tags in the database.
    # if type(data_dict['tags_predefined']) ==  type([]):
    #     data_dict['tags'] = convert_to_tags_format(data_dict['tags_predefined'])
    # else:
    #     # because CKAN always returns strings we need to handle it in order to
    #     # pass it to the covert_to_tags_format function.
    #     # This is done in order to aviod an error happening on resource_create.
    #     tags_predefined = data_dict['tags_predefined'].strip('}').strip('{').split(',')
    #     data_dict['tags'] = convert_to_tags_format(tags_predefined)

    dataset_dict = core_package_update(context, data_dict)

    return dataset_dict

@toolkit.side_effect_free
def package_activity_list(context, data_dict):
    '''Override core ckan package_activity_list
    '''
    get_workflow_activities = data_dict.get('get_workflow_activities')
    full_list = core_package_activity_list(context, data_dict)
    workflow_activities = [
        a for a in full_list if 'workflow_activity' in a.get('data', {})]
    normal_activities = [
        a for a in full_list if 'workflow_activity' not in a.get('data', {})]
    # Filter out the activities that are related `approval_state`
    normal_activities = list(filter(
        lambda activity: core_activity_detail_list(
            context, {'id': activity['id']}).pop()
            .get('data', {})
            .get('package_extra', {})
            .get('key') != 'approval_state', normal_activities))
    return (workflow_activities
        if get_workflow_activities else normal_activities)


@toolkit.side_effect_free
def dashboard_activity_list(context, data_dict):
    '''Override core ckan dashboard_activity_list
    '''
    full_list = core_dashboard_activity_list(context, data_dict)
    normal_activities = [
        a for a in full_list if 'workflow_activity' not in a.get('data', {})]
    return normal_activities


@toolkit.side_effect_free
def group_activity_list(context, data_dict):
    '''Override core ckan group_activity_list
    '''
    full_list = core_group_activity_list(context, data_dict)
    normal_activities = [
        a for a in full_list if 'workflow_activity' not in a.get('data', {})]
    return normal_activities


@toolkit.side_effect_free
def recently_changed_packages_activity_list(context, data_dict):
    '''Override core ckan recently_changed_packages_activity_list
    '''
    full_list = core_recently_changed_packages_activity_list(context, data_dict)
    normal_activities = [
        a for a in full_list if 'workflow_activity' not in a.get('data', {})]
    return normal_activities
