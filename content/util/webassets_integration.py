class Integration:
    def __init__(self, env):
        """
        :type env: webassets.Environment
        """
        self.env = env

    def asset_url(self, bundle_name):
        """
        :type bundle_name: str
        """
        urls = self.env[bundle_name].urls()
        return "/{}".format(urls[0])  # /{} to make url absolute

    def register(self, app):
        app.jinja_env.globals.update(asset_url=self.asset_url)

