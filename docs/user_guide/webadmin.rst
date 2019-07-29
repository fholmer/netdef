
Webadmin
========

Webadmin is a simple web interface to configure and debug your application.
You can customize basic behavour in ``default.conf``:

Here is a basic example:

.. code-block:: ini

    [webadmin]
    host = 0.0.0.0
    port = 8000
    user = admin
    password = 
    password_hash = pbkdf2:sha256:150000$$N2b3ky8d$$51fbf24e48d498bd5543d60a86bd94927fd4d6eb123bf2d81a7401666eeea5c0
    secret_key = 1b50383ec6945aff8993f018feb568fa
    on = 1
    home_on = 1
    config_on = 1
    installationrepo_on = 1
    tools_on = 1
    settings_on = 1
    sources_on = 1
    expressions_on = 1
    statistics_on = 1
    ssl_certificate = 
    ssl_certificate_key = 
    ssl_on = 0

.. list-table:: [webadmin]
   :header-rows: 1
   :widths: 15 15 70
   
   * - Config
     - Default
     - Description
   * - host
     - 0.0.0.0
     - Webserver host address
   * - port
     - 8000
     - Webserver tcp port
   * - user
     - admin
     - Username
   * - password
     - 
     - Plain text password. If password_hash is set then this option is ignored.
   * - password_hash
     - 
     - Password hash generated with ``python -m netdef -ga`` command
   * - secret_key
     - 
     - Secret flask session key. Can be generated with ``python -m netdef -ga``
   * - on
     - 1
     - Enable Webadmin.

       * **0** -- disabled.
       * **1** -- enabled.
       
   * - home_on
     - 1
     - Enable :menuselection:`Webadmin-->Home`.
   * - config_on
     - 1
     - Enable :menuselection:`Webadmin-->Config`.
   * - installationrepo_on
     - 1
     - Enable :menuselection:`Webadmin-->Tools-Update`.
   * - tools_on
     - 1
     - Enable :menuselection:`Webadmin-->Tools`.
   * - settings_on
     - 1
     - Enable :menuselection:`Webadmin-->Settings`.
   * - sources_on
     - 1
     - Enable :menuselection:`Webadmin-->Sources`.
   * - expressions_on
     - 1
     - Enable :menuselection:`Webadmin-->Expressions`.
   * - statistics_on
     - 1
     - Enable :menuselection:`Webadmin-->Statistics`.
   * - ssl_certificate
     - 
     - File path to ssl certificate. Required if ``ssl_on=1``.
   * - ssl_certificate_key
     - 
     - File path to ssl certificate key. Required if ``ssl_on=1``.
   * - ssl_on
     - 0
     - Enable https.


Override root endpoint
----------------------

A common use case is to integrate an existing flask app into the root endpoint
(/) of the webserver. The example shows how this is done by retrieving the
webadmin WSGI app and register a new endpoint at '/'

``first_app/main.py``::

    # function that register my custom flask app
    def init_app(app):
        @app.route('/')
        def hello_world():
            return 'Hello, World!'
        return app

    def main():
        ...

        engine = ThreadedWebGuiEngine.ThreadedWebGuiEngine(shared)

        # init my custom flask app as soon as the webgui engine is initialized.
        init_app(engine.get_flask_app())

        engine.add_controller_classes(controllers)
        engine.add_source_classes(sources)
        engine.add_rule_classes(rules)
        engine.load([__package__, 'netdef'])
        engine.init()
        engine.start()
        engine.block() # until ctrl-c or SIG_TERM
        engine.stop()
        ...

Override :menuselection:`Webadmin-->Home`
-----------------------------------------

Copy the default html template.

``netdef/Engines/templates/home.html``:

.. literalinclude:: ../../netdef/Engines/templates/home.html
   :language: jinja

Paste it into your application with extended information:

``first_app/Engines/templates/home.html``:

..  code-block:: jinja
    :linenos:
    :emphasize-lines: 6, 7, 8

    {% extends 'home/home.html' %}

    {% block home %}

            <p>{{app_name}} version: {{app_version}}</p>
            <p>netdef version: {{netdef_version}}</p>
            <p>Python version: {{py_version}}</p>
            <p>Platform version: {{sys_version}}</p>

    {% endblock home %}




Now you only have to override the Home View by creating following file:

``first_app/Engines/webadmin/Home.py``:

..  code-block:: python
    :linenos:
    :emphasize-lines: 13, 17

    import sys
    import datetime
    import platform
    from flask import current_app
    from flask_admin import expose

    from netdef.Engines.webadmin import Views, Home

    from netdef import __version__ as netdef_version
    from ... import __version__ as app_version
    from ... import __package__ as app_name

    @Views.register("Home")
    def setup(admin):
        Home.setup(admin, MyNewHome(name='Home', endpoint='home'))

    class MyNewHome(Home.Home):
        @expose("/")
        def index(self):
            return self.render(
                'home.html',
                app_name=app_name,
                app_version=app_version,
                netdef_version=netdef_version,
                py_version=sys.version,
                sys_version=str(platform.version())
            )

- At line 13 we replace the default :menuselection:`Webadmin-->Home` with your own
- At line 17 we override the default Home class with our extended functionality


Override :menuselection:`Webadmin-->Tools`
------------------------------------------

Copy the default html template.

``netdef/Engines/templates/tools.html``:

.. literalinclude:: ../../netdef/Engines/templates/tools.html
   :language: jinja

Paste it into your application with extended information:

``first_app/Engines/templates/tools.html``:

..  code-block:: jinja
    :linenos:

    {% extends 'tools/tools.html' %}
    {% block system_panel %}
            <div class="panel panel-default">
                <div class="panel-heading">System</div>
                <div class="panel-body">
                    <p>Uptime: {{sys_uptime}}</p>
                    <div class="container">
                        <div class="row">
                            <a href="./cmd_dir/" class="btn btn-default col-md-2" role="button">
                                <span class="glyphicon glyphicon-list" aria-hidden="true"></span>
                                dir
                            </a>
                        </div>
                    </div>
                </div>
            </div>
    {% endblock system_panel %}

Now you only have to override the Tools View by creating following file:

``first_app/Engines/webadmin/Tools.py``:

..  code-block:: python
    :linenos:
    :emphasize-lines: 5, 9

    from flask import stream_with_context, Response
    from flask_admin import expose
    from netdef.Engines.webadmin import Views, Tools

    @Views.register("Tools")
    def setup(admin):
        Tools.setup(admin, MoreTools(name='Tools', endpoint='tools'))

    class MoreTools(Tools.Tools):
        @expose("/cmd_dir/")
        def hg_log(self):
            return Response(
                stream_with_context(
                    Tools.stdout_from_terminal_as_generator(
                        "dir",
                        pre="Command:\n\n   hg log -r .:\n\nResult:\n\n",
                        post=""
                    )
                )
            )

- At line 5 we replace the default :menuselection:`Webadmin-->Tools` with your own
- At line 9 we override the default Tools class with our extended functionality
