import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper


class RaseelThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
   

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'raseel_theme')

    
    # IRoutes
    def before_map(self, map):
        '''
        Map custom controllers and endpoints
        '''
        publish_controller = 'ckanext.raseel_theme.controller:StateUpdateController'
        map.connect('dataset.workflow', '/dataset/workflow/{id}',
                    controller='ckanext.raseel_theme.controller:WorkflowActivityStreamController',
                    action='list_activities')
        map.connect('dashboard.requests', '/dashboard/requests',
                    controller='ckanext.raseel_theme.controller:PendingRequestsController',
                    action='list_requests')
        map.connect('dashboard.topics', '/dashboard/topics',
                    controller='ckanext.raseel_theme.controller:DashboardTopicsController',
                    action='list_groups')
        map.connect('/dataset-publish/{id}/approve',
                    controller=publish_controller,
                    action='approve')
        map.connect('/dataset-publish/{id}/reject',
                    controller=publish_controller,
                    action='reject')
        map.connect('/dataset-publish/{id}/resubmit',
                    controller=publish_controller,
                    action='resubmit')
        map.connect(
            'download_zip',
            '/download/zip/{zip_id}',
            controller='ckanext.raseel_theme.controller:DownloadController',
            action='download_zip'
        )

        map.connect('help_url',
                    '/help',
                    controller='ckanext.raseel_theme.controller:HelpController',
                    action="external_help")

        map.connect('/user/logged_in',
                    controller='ckanext.raseel_theme.controller:CustomeUserController',
                    action="logged_in")

        ## Docs
        map.connect('/dataset/new_resource/{id}',
                    controller='ckanext.raseel_theme.controller:NewResourceController',
                    action='new_resource')
        map.connect('doc',
                    '/dataset/new_doc/{id}',
                    controller='ckanext.raseel_theme.controller:NewResourceController',
                    action='new_doc')

        map.connect('dataset.docs', '/dataset/docs/{id}',
                    controller='ckanext.raseel_theme.controller:DocumentationController',
                    action='read_doc')

        map.connect('/dataset/docs/{dataset_id}/pin/{resource_id}',
                    controller='ckanext.raseel_theme.controller:DocumentationController',
                    action='pin')

        map.connect('/dataset/docs/{dataset_id}/unpin/{resource_id}',
                    controller='ckanext.raseel_theme.controller:DocumentationController',
                    action='unpin')

        map.connect('dataset.disqus', '/dataset/{id}/disqus',
                    controller='ckanext.raseel_theme.controller:DisqusController',
                    action='read_disqus')

        ## package
        map.connect('dataset.new','/dataset/new',
                    controller='ckan.controllers.package:PackageController',
                    action='new')
        map.connect('/dataset/{id}',
                    controller='ckanext.raseel_theme.controller:RaseelPackageController',
                    action='read')

        # Rename organizations
        map.redirect('/organization', '/publisher',
                     _redirect_code='301 Moved Permanently')
        map.redirect('/organization/{url}?{qq}', '/publisher/{url}{query}',
                     _redirect_code='301 Moved Permanently')
        org_controller = 'ckanext.raseel_theme.controller:RaseelOrganizationController'

        with routes.mapper.SubMapper(map, controller=org_controller) as m:
            m.connect('publisher_index', '/publisher', action='index')
            m.connect('/publisher/list', action='list')
            m.connect('/publisher/new', action='new')
            m.connect('/publisher/{action}/{id}',
                      requirements=dict(action='|'.join([
                          'delete',
                          'admins',
                          'member_new',
                          'member_delete',
                          'history'
                          'followers',
                          'follow',
                          'unfollow',
                      ])))
            m.connect('publisher_activity', '/publisher/activity/{id}',
                      action='activity', ckan_icon='time')
            m.connect('publisher_read', '/publisher/{id}', action='read')
            m.connect('publisher_about', '/publisher/about/{id}',
                      action='about', ckan_icon='info-sign')
            m.connect('publisher_read', '/publisher/{id}', action='read',
                      ckan_icon='sitemap')
            m.connect('publisher_edit', '/publisher/edit/{id}',
                      action='edit', ckan_icon='edit')
            m.connect('publisher_members', '/publisher/edit_members/{id}',
                      action='members', ckan_icon='group')
            m.connect('publisher_bulk_process',
                      '/publisher/bulk_process/{id}',
                      action='bulk_process', ckan_icon='sitemap')

        map.connect('stats_json', '/stats/json',
                    controller='ckanext.raseel_theme.controller:RaseelStatsController',
                    action='index', ckan_icon='info-sign')

        # Rename groups / categories to topics
        map.redirect('/group', '/topic',
                     _redirect_code='301 Moved Permanently')
        map.redirect('/group/{url:.*}', '/topic/{url}',
                     _redirect_code='301 Moved Permanently')
        group_controller = 'ckanext.raseel_theme.controller:RaseelTopicController'

        with routes.mapper.SubMapper(map, controller=group_controller) as m:
            m.connect('topic_index', '/topic', action='index')
            m.connect('/topic/list', action='list')
            m.connect('/topic/new', action='new')
            m.connect('/topic/{action}/{id}',
                    requirements=dict(action='|'.join([
                        'delete',
                        'admins',
                        'member_new',
                        'member_delete',
                        'history'
                        'followers',
                        'follow',
                        'unfollow',
                    ])))
            m.connect('topic_activity', '/topic/activity/{id}',
                    action='activity', ckan_icon='time')
            m.connect('topic_read', '/topic/{id}', action='read')
            m.connect('topic_about', '/topic/about/{id}',
                    action='about', ckan_icon='info-sign')
            m.connect('topic_read', '/topic/{id}', action='read',
                    ckan_icon='sitemap')
            m.connect('topic_edit', '/topic/edit/{id}',
                    action='edit', ckan_icon='edit')
            m.connect('topic_members', '/topic/edit_members/{id}',
                    action='members', ckan_icon='group')
            m.connect('topic_bulk_process',
                    '/topic/bulk_process/{id}',
                    action='bulk_process', ckan_icon='sitemap')

        with routes.mapper.SubMapper(map, controller='package') as m:
            m.connect('dataset_topics', '/dataset/topics/{id}',
                      action='groups', ckan_icon='users')

        return map

    # IValidators
    def get_validators(self):
        '''
        Define custom validators
        '''
        return {
            'state_validator': validators.state_validator,
            'resource_type_validator': validators.resource_type_validator,
            'dummy_validator': validators.dummy_validator,
            'package_name_validator': validators.package_name_validator
        }

    def dataset_facets(self, facets_dict, package_type):
        '''
        Override core search fasets for datasets
        '''
        from collections import OrderedDict
        facets_dict = OrderedDict({})
        facets_dict['groups'] = "Major Topics"
        facets_dict['tags'] = "Tags"
        facets_dict['organization'] = "Publishers"
        facets_dict['res_format'] = "Formats"
        facets_dict['spatial'] = "Geography"
        facets_dict['license_id'] = "License"
        facets_dict['level_of_data_string'] = "Level Of Data"
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        '''
        Override core search fasets for publishers
        '''
        facets_dict['organization'] = 'Publishers'
        facets_dict['groups'] = 'Topics'
