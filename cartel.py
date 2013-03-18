"""
An App to auto login at Cartel Coffee Lab.

Authors: J. Matt Peterson
         Craig J. Bishop


Source: https://github.com/jmatt/cartell

Thanks: http://stackoverflow.com/users/113314/ryan
See: http://stackoverflow.com/questions/4994058/pyobjc-tutorial-without-xcode

"""
import logging
import socket
import time
import urllib2

from AppKit import NSApplication, NSStatusBar, NSBundle,\
    NSImage, NSMenu, NSMenuItem, NSObject,\
    NSLog, NSTimer, NSVariableStatusItemLength,\
    NSWorkspace
from Foundation import NSNotificationCenter
from PyObjCTools import AppHelper
from SystemConfiguration import CFRunLoopGetCurrent, kCFRunLoopCommonModes,\
    kCFRunLoopDefaultMode, kSCNetworkFlagsInterventionRequired,\
    SCNetworkReachabilityCreateWithAddress, SCNetworkReachabilityGetFlags,\
    SCNetworkReachabilityScheduleWithRunLoop,\
    SCNetworkReachabilityUnscheduleFromRunLoop,\
    SCNetworkReachabilitySetCallback

from mechanize import Browser


ICON_BASE = "Coffee Cup Icon Black"
ICON_EXT = "icns"
ICON_FILE = ICON_BASE + "." + ICON_EXT
MAX_ATTEMPTS = 3
kReachabilityChangedNotification = "kNetworkReachabilityChangedNotification"


def reachabilityCallback(target, flags, info):
    NSLog("reachability!")
    NSLog("flags = %s" % str(flags))
    NSLog("kSCNetworkFlagsInterventionRequired = %s" % (flags & kSCNetworkFlagsInterventionRequired))
    default = NSNotificationCenter.defaultCenter()
    default.postNotificationName_object_(kReachabilityChangedNotification, info)


class Reachability(NSObject):
    """
    Handle Notifications from the network.
    """

    app = None

    def startNotifier(self, callback=reachabilityCallback):
        inet_addr =  "8.8.8.8"
        self.loop = CFRunLoopGetCurrent()
        
        self.target = SCNetworkReachabilityCreateWithAddress(None, (inet_addr, 80))
        SCNetworkReachabilitySetCallback(self.target, callback, inet_addr)
        
        ok, flags = SCNetworkReachabilityGetFlags(self.target, None)

        if ok:
            callback(self.target, flags, inet_addr)

        SCNetworkReachabilityScheduleWithRunLoop(
            self.target,
            self.loop,
            kCFRunLoopCommonModes)

    def stopNotifier(self):
        self.loop = CFRunLoopGetCurrent()
        SCNetworkReachabilityUnscheduleFromRunLoop(
            self.target,
            self.loop,
            kCFRunLoopDefaultMode)

    def handleChange_(self, notification):
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

        # Wire up hibernate and cna launch events
        self.workspace = NSWorkspace.sharedWorkspace()
        self.default_center = NSNotificationCenter.defaultCenter()

        self.reachability = Reachability.new()
        self.reachability.startNotifier()
        self.reachability.app = self

        self.default_center.addObserver_selector_name_object_(
            self.reachability,
            "handleChange:",
            kReachabilityChangedNotification,
            None)

    def connectAndCloseCNA_(self, notification):
        success = self.connect_(notification)
        if success:
            self.terminateCNA()

    def connect_(self, notification):
        """
        Connect to the wifi network.

        If you cannot connect to the internet then attempt to login to
        the wifi network. If the attempt fails retry MAX_ATTEMPTS
        many times.
        """
        NSLog('Connect, damn it.')
        attempts = 0
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
            except urllib2.URLError as e:
                NSLog("Attempts[%s/%s] Problem trying to connect. %s." 
                    % (attempts, MAX_ATTEMPTS, e.message))
                time.sleep(1)
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
