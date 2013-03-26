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

from httplib import HTTPException
from mechanize import Browser
from urllib2 import URLError

from reach.Reachability import Reachability,\
    kReachabilityChangedNotification

ICON_BASE = "Coffee Cup Icon Black"
ICON_EXT = "icns"
ICON_FILE = ICON_BASE + "." + ICON_EXT
MAX_ATTEMPTS = 12


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
                br = Browser()
                br.set_handle_robots(False)
                r = br.open("http://www.apple.com/library/test/success.html")
                content = r.read()
                if "Welcome to Cartel Campbell Ave" in content:
                    NSLog("Trying to connect...")
                    try:
                        br.select_form(nr=0)
                        br.form["auth_pass"] = "cartel"
                        r = br.submit()
                        if r.code == 200:
                            NSLog("Success!")  # connnected.
                            return True
                    except Exception as e:
                        NSLog("Problem trying to connect.")
                else:
                    NSLog("Looks like you are already connected.")
                    return True
            except (HttpException, URLError) as e:
                NSLog("Attempts[%s/%s] Problem trying to connect. %s." 
                    % (attempts, MAX_ATTEMPTS, e.message))
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
