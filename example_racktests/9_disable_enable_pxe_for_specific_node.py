from strato.racktest.infra.suite import *
import example_plugins.ping
import logging
import time


class Test:
    MAX_TIME_FOR_NODE_TO_ANSWER_PING_AFTER_BOOTING_FROM_PXE = 240
    HOSTS = dict(pxeserver=dict(rootfs="rootfs-basic"), pxeclient=dict(rootfs="rootfs-basic"))

    def run(self):
        TS_ASSERT(self._isClientPingable())
        host.pxeclient.node.disablePXE()
        logging.progress("PXE has been disabled for %s", host.pxeclient.node.primaryMACAddress())
        host.pxeclient.node.coldRestart()
        logging.progress("Client is being rebooted. sleeping for %d seconds to make sure client stays down",
                        self.MAX_TIME_FOR_NODE_TO_ANSWER_PING_AFTER_BOOTING_FROM_PXE )
        time.sleep(self.MAX_TIME_FOR_NODE_TO_ANSWER_PING_AFTER_BOOTING_FROM_PXE)
        TS_ASSERT_EQUALS(self._isClientPingable(), False)
        logging.progress("Client is not reachable. looks like its PXE has been disabled successfully")
        host.pxeclient.node.enablePXE()
        logging.progress("PXE has been enabled for %s", host.pxeclient.node.primaryMACAddress())
        host.pxeclient.node.coldRestart()
        logging.progress("Client is being rebooted. making sure that client is booting nicely")
        TS_ASSERT_PREDICATE_TIMEOUT(self._isClientPingable,
                                    TS_timeout = self.MAX_TIME_FOR_NODE_TO_ANSWER_PING_AFTER_BOOTING_FROM_PXE)

    def _isClientPingable(self):
        try:
            host.pxeserver.ping.once(host.pxeclient)
        except Exception as ex:
            if "100% packet loss" in ex.message:
                pingable = False
            else:
                raise
        else:
            pingable = True
        return pingable

    def tearDown(self):
        logging.progress("enabling PXE for %s", host.pxeclient.node.primaryMACAddress())
        host.pxeclient.node.enablePXE()
