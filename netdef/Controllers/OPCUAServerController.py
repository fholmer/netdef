import logging
import datetime
import werkzeug.security
from opcua import Server, ua
from opcua.common.callback import CallbackType
from opcua.common import utils
from opcua.server.internal_server import InternalServer, InternalSession
from opcua.server.user_manager import UserManager
from netdef.Controllers import BaseController, Controllers
from netdef.Sources.BaseSource import StatusCode

class CustomInternalSession(InternalSession):
    def activate_session(self, params):
        id_token = params.UserIdentityToken
        if isinstance(id_token, ua.AnonymousIdentityToken):
            raise utils.ServiceError(ua.StatusCodes.BadUserAccessDenied)
        return super().activate_session(params)

class CustomInternalServer(InternalServer):
    def set_parent(self, parent):
        self._parent = parent
    def create_session(self, name, user=UserManager.User.Anonymous, external=False):
        return CustomInternalSession(self, self.aspace, self.subscription_service, name, user=user, external=external)

@Controllers.register("OPCUAServerController")
class OPCUAServerController(BaseController.BaseController):
    """
    This Controller will start a freeopcua server instance and will
    add a nodeid for all sources received in ADD_SOURCE messages.
    
    When a client writes a new value this event will be forwarded to
    the associated source and a RUN_EXPRESSION message will be sent.

    When a WRITE_SOURCE message is received the value for the associated
    source will be updated in the server and all connected clients will
    receive a value update
    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")

        self.shared.config.set_hidden_value(self.name, "user")
        self.shared.config.set_hidden_value(self.name, "password")
        self.shared.config.set_hidden_value(self.name, "password_hash")

        def config(key, val):
            return self.shared.config.config(self.name, key, val)

        endpoint = config("endpoint", "no_endpoint")
        certificate = config("certificate", "")
        private_key = config("private_key", "")
        uri = config("uri", "http://examples.freeopcua.github.io")
        root_object_name = config("root_object_name", "TEST")
        separator = config("separator", ".")
        namespace = config("namespace", 2)

        self.oldnew = config("oldnew_comparision", 0)

        self.strict_datatypes = config("strict_datatypes", 1)

        admin_username = config("user", "admin")
        admin_password = config("password", "admin")
        admin_password_hash = config("password_hash", "").replace("$$", "$")

        anonymous_on = config("anonymous_on", 0)
        username_on = config("username_on", 1)
        full_encryption_on = config("full_encryption_on", 1)

        initial_values_is_quality_good = config("initial_values_is_quality_good", 0)

        if anonymous_on:
            server = Server()
        else:
            server = Server(iserver=CustomInternalServer())
            server.iserver.set_parent(server)

        server.set_endpoint(endpoint)
        server.allow_remote_admin(False)

        if certificate and private_key:
            server.load_certificate(str(certificate))
            server.load_private_key(str(private_key))

        if username_on:
            server.set_security_IDs(["Username"])

        if full_encryption_on:
            server.set_security_policy([
                    ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                    ua.SecurityPolicyType.Basic256Sha256_Sign])
        
        def custom_user_manager(isession, userName, password):
            if userName != admin_username:
                return False
            if admin_password_hash:
                if werkzeug.security.check_password_hash(admin_password_hash, password):
                    return True
            else:
                # fallback til plaintext
                if password == admin_password:
                    return True
            return False

        if username_on:
            server.user_manager.set_user_manager(custom_user_manager)

        idx = server.register_namespace(uri)
        objects = server.get_objects_node()
        root = objects.add_object(idx, root_object_name)

        self.server = server
        self.objects = objects
        self.root = root
        self.sep = separator
        self.ns = namespace
        self.items = []

        if initial_values_is_quality_good:
            self.initial_status_code = ua.StatusCodes.Good
        else:
            self.initial_status_code = ua.StatusCodes.BadNoData


    def run(self):
        self.logger.info("Running")
        self.server.start()
        self.server.subscribe_server_callback(CallbackType.ItemSubscriptionCreated, self.create_monitored_items)
        self.server.subscribe_server_callback(CallbackType.ItemSubscriptionModified, self.modify_monitored_items)

        subhandler = SubHandler(self)
        self.subscription = self.server.create_subscription(100, subhandler)

        while not self.has_interrupt():
            self.loop_incoming() # denne kaller opp handle_* funksjonene

        self.server.stop()
        self.logger.info("Stopped")


    def get_default_value(self, incoming):
        "Returns the default value of the source value"
        defaultvalue = incoming.interface(incoming.value).value
        return defaultvalue


    def handle_add_source(self, incoming):
        "Add a source to the server"
        nodeid = self.get_nodeid(incoming)
        self.logger.debug("'Add source' event for nodeid: %s", nodeid)
        if self.has_source(nodeid):
            self.logger.error("source already exists %s", nodeid)
            return

        defaultvalue = self.get_default_value(incoming)
        varianttype = self.get_varianttype(incoming)
        varnode = self.add_variablenode(self.root, nodeid, defaultvalue, varianttype)

        if self.is_writable(incoming):
            varnode.set_writable()

        self.add_source(nodeid, (incoming, varnode))
        self.subscription.subscribe_data_change(varnode)


    def handle_write_source(self, incoming, value, source_time):
        "Receive a value change from an expression and update the server"
        self.logger.debug("'Write source' event to %s. value: %s at %s", incoming.key, value, source_time)
        nodeid = self.get_nodeid(incoming)
        incoming, varnode = self.get_source(nodeid)
        varnode.set_value(value)


    def add_folder(self, parent, foldername):
        "Add a folder in server"
        if not parent:
            parent = self.root
        return parent.add_folder(self.ns, foldername)


    def add_variablenode(self, parent, ref, val, varianttype):
        "Create and add a variable in server and return the variable node"
        self.logger.debug("ADDING %s AS %s" % (ref, varianttype))
        if not parent:
            parent = self.root

        nodeid = ua.NodeId.from_string(ref)

        datavalue = self.create_datavalue(
            val,
            varianttype,
            self.initial_status_code
        )
        var_node = parent.add_variable(
            nodeid=ref,
            bname="%d:%s" % (nodeid.NamespaceIndex, nodeid.Identifier),
            val=None,
            varianttype=varianttype
        )
        var_node.set_data_value(datavalue)
        return var_node


    def create_datavalue(self, val, datatype, statuscode):
        "Create a value for the server that keep the correct datatype"
        variant = ua.Variant(value=val, varianttype=datatype)
        status = ua.StatusCode(statuscode)
        return ua.DataValue(variant=variant, status=status)


    def get_varianttype(self, incoming):
        "Returns the varianttype from the source"
        if hasattr(incoming, "get_varianttype"):
            return getattr(incoming, "get_varianttype")()
        else:
            return None


    def get_nodeid(self, incoming):
        "Returns the nodeid from the source"
        if hasattr(incoming, "get_nodeid"):
            return getattr(incoming, "get_nodeid")()
        else:
            return incoming.key
    

    def is_writable(self, incoming):
        "Returns True if source is writable for the opcua client"
        if hasattr(incoming, "is_writable"):
            return True if getattr(incoming, "is_writable")() else False
        else:
            return True


    def send_datachange(self, nodeid, value, stime, status_ok, ua_status_code):
        "Triggers a RUN_EXPRESSION message for given source"
        if self.has_source(nodeid):
            item, varnode = self.get_source(nodeid)
            if not status_ok:
                if item.status_code == StatusCode.NONE:
                    if ua_status_code == self.initial_status_code:
                        # we are actually good
                        status_ok = True

            if self.update_source_instance_value(item, value, stime, status_ok, self.oldnew):
                self.send_outgoing(item)


    def modify_monitored_items(self, event, dispatcher):
        self.logger.info('modify_monitored_items')


    def create_monitored_items(self, event, dispatcher):
        "write a warning to logfile if the client add a nodeid that does not exists"
        for idx in range(len(event.response_params)):
            if not event.response_params[idx].StatusCode.is_good():
                nodeId = event.request_params.ItemsToCreate[idx].ItemToMonitor.NodeId
                #print (idx, nodeId.NamespaceIndex, nodeId.Identifier, nodeId.NamespaceUri, nodeId.NodeIdType)
                ident = nodeId.to_string()
                self.logger.warning("create_monitored_items: missing %s", ident)


class SubHandler():
    """
    The subscription handler for the server. Will send value changes i server to the controller.
    """
    def __init__(self, controller):
        self.controller = controller
        self.logger = self.controller.logger


    def datachange_notification(self, node, val, data):
        nodeid = node.nodeid.to_string()
        item = data.monitored_item.Value
        source_value = item.Value.Value
        source_time = item.SourceTimestamp
        source_status_ok = item.StatusCode.value == 0
        self.logger.debug("nodeid:%s, value:%s, time:%s, ok:%s, uacode:%s", nodeid, source_value, source_time, source_status_ok, item.StatusCode.value)
        self.controller.send_datachange(nodeid, source_value, source_time, source_status_ok, item.StatusCode.value)


    def event_notification(self, event):
        self.logger.info("Python: New event %s", event)
