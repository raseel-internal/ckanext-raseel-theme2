import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class RaseelThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'raseel_theme')  
    
    def get_blueprint(self):
        """
        CKAN uses Flask Blueprints in the /ckan/views dir for user and dashboard
        Here we override some routes to redirect unauthenticated users to the logout page, and only redirect the
        user to the `came_from` URL if they are logged in.
        :return:
        """
        from .views import user
        blueprints = user.get_blueprints()
        return blueprints
    
