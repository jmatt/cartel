"""
An App to auto login at Cartel Coffee Lab.

Authors: J. Matt Peterson
         Craig J. Bishop


Source: https://github.com/jmatt/cartel

Thanks: http://stackoverflow.com/users/113314/ryan

See: https://github.com/jmatt/reach
     http://stackoverflow.com/questions/4994058/pyobjc-tutorial-without-xcode
     https://bitbucket.org/wolfg/pyobjc/src/5bc325e5bca4/
...  pyobjc-framework-SystemConfiguration/Examples/CallbackDemo/interneton.py

"""
import logging
import socket
import time

from AppKit import NSApplication, NSStatusBar, NSBundle,\
    NSImage, NSMenu, NSMenuItem, NSObject,\
    NSLog, NSTimer, NSVariableStatusItemLength,\
    NSWorkspace
from Foundation import NSNotificationCenter
from PyObjCTools import AppHelper

import requests
from requests.exceptions import ConnectionError

from reach.Reachability import Reachability,\
    kReachabilityChangedNotification

ICON_BASE = "Coffee Cup Icon Black"
ICON_EXT = "icns"
ICON_FILE = ICON_BASE + "." + ICON_EXT
MAX_ATTEMPTS = 2
URL = "http://192.168.3.1:8000/?redirurl=http%3A%2F%2Fwww.apple.com%2Ftest%2Ftest%2Fsuccess.html"
DATA = {"redirurl": "http://www.aplle.com/test/test/success.html",
        "auth_user": "cartel",
        "auth_pass": "cartel",
        "accept": "Continue"}


class ReachabilityHandler(NSObject):
    """
    Handle reachability notifications from the network.
    """

    app = None

    def handleChange_(self, notification):
        """
        Handle Reachability changes with the CartelApp.
        """
        try:
            NSLog("change!")
            NSLog(str(notification))
            self.app.connectAndCloseCNA_(self)
        except:
            logging.debug("exception... network change!")


class CartelApp(NSApplication):
    """
    The main gui for the Cartel Login app.
    """

    def finishLaunching(self):
        # Make statusbar item
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(
            NSVariableStatusItemLength)
        # Thanks Matthias Kretschmann
        # at http://kremalicious.com/coffee-cup-icon/
        icon_path = NSBundle.mainBundle()\
                            .pathForResource_ofType_(
                                ICON_BASE, ICON_EXT)
        if not icon_path:
            icon_path = ICON_FILE
        self.icon = NSImage.alloc()\
                           .initByReferencingFile_(icon_path)
        self.icon.setScalesWhenResized_(True)
        self.icon.setSize_((20, 20))
        self.statusitem.setImage_(self.icon)

        # Make the menu
        self.menubarMenu = NSMenu.alloc().init()

        self.menuItem = NSMenuItem.alloc()\
                                  .initWithTitle_action_keyEquivalent_(
                                      'Connect', 'connectAndCloseCNA:', '')
        self.menubarMenu.addItem_(self.menuItem)

        self.quit = NSMenuItem.alloc()\
                              .initWithTitle_action_keyEquivalent_(
                                  'Quit', 'terminate:', '')
        self.menubarMenu.addItem_(self.quit)

        # Add menu to statusitem
        self.statusitem.setMenu_(self.menubarMenu)
        self.statusitem.setToolTip_('Cartel')
        self.statusitem.setHighlightMode_(True)

        # Get the default notification center.
        self.workspace = NSWorkspace.sharedWorkspace()
        self.default_center = NSNotificationCenter.defaultCenter()

        # Create the handler
        self.rhandler = ReachabilityHandler.new()
        self.rhandler.app = self

        self.default_center.addObserver_selector_name_object_(
            self.rhandler,
            "handleChange:",
            kReachabilityChangedNotification,
            None)

        # Create the reachability object and start notifactions.
        self.reachability = Reachability()
        self.reachability.startNotifier()

    def connectAndCloseCNA_(self, notification):
        success = self.connect_(notification)
        if success:
            self.terminateCNA()

    def wait_increment(self, wait):
        if wait < 32:
            return wait * 2
        else:
            return 32

    def try_connect_(self, url=None, data=None):
        if not url:
            url = URL
        if not data:
            data = DATA
        try:
            resp = requests.post(url,
                                 data=data,
                                 allow_redirects=False)
            if resp.ok:
                NSLog("Success!")  # connnected.
                return True
        except ConnectionError as e:
            if e.args and len(e.args)\
                and "www.cartelcoffeelab.com" in e.args[0].message:
                return True
            else:
                raise e

    def connect_(self, notification):
        """
        Connect to the wifi network.

        If you cannot connect to the internet then attempt to login to
        the wifi network. If the attempt fails retry MAX_ATTEMPTS
        many times.
        """
        NSLog('Connect, damn it.')
        attempts = 0
        wait = 1
        while attempts < MAX_ATTEMPTS:
            try:
                attempts += 1
                if self.try_connect_():
                    return True
            except ConnectionError as e:
                NSLog("Attempts[%i/%i] Problem trying to connect. %s." %
                      (attempts, MAX_ATTEMPTS, e.message))
                time.sleep(wait)
                wait = self.wait_increment(wait)
        return False

    def terminateCNA(self):
        """
        Terminate the CaptiveNetworkAssistant if it's running.
        """
        apps = self.workspace.runningApplications()
        for a in apps:
            bundle_id = a.valueForKey_("bundleIdentifier")
            # For dev use "com.sublimetext.3" or "org.gnu.Emacs", etc.
            if bundle_id == "com.apple.CaptiveNetworkAssistant":
                NSLog("Cartel is Terminating CNA.")
                a.terminate()


if __name__ == "__main__":
    app = CartelApp.sharedApplication()
    AppHelper.runEventLoop()
