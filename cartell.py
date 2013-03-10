"""
A service to auto login at Cartel Coffee Lab.

Thanks: http://stackoverflow.com/users/113314/ryan
See: http://stackoverflow.com/questions/4994058/pyobjc-tutorial-without-xcode

"""
import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper
import mechanize


class CartellApp(NSApplication):

    def finishLaunching(self):
        # Make statusbar item
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(
            NSVariableStatusItemLength)
        # Thanks Matthias Kretschmann
        # at http://kremalicious.com/coffee-cup-icon/
        self.icon = NSImage.alloc().initByReferencingFile_(
            'Coffee Cup Icon Black.icns')
        self.icon.setScalesWhenResized_(True)
        self.icon.setSize_((20, 20))
        self.statusitem.setImage_(self.icon)

        #make the menu
        self.menubarMenu = NSMenu.alloc().init()

        self.menuItem = NSMenuItem.alloc()\
                                  .initWithTitle_action_keyEquivalent_(
                                      'Connect', 'connect:', '')
        self.menubarMenu.addItem_(self.menuItem)

        self.quit = NSMenuItem.alloc()\
                              .initWithTitle_action_keyEquivalent_(
                                  'Quit', 'terminate:', '')
        self.menubarMenu.addItem_(self.quit)

        #add menu to statusitem
        self.statusitem.setMenu_(self.menubarMenu)
        self.statusitem.setToolTip_('Cartell')

    def connect_(self, notification):
        NSLog('Connect, damn it.')
        br = mechanize.Browser()
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
            except Exception as e:
                NSLog("Problem trying to connect.")
        else:
            NSLog("Looks like you are already connected.")

if __name__ == "__main__":
    app = CartellApp.sharedApplication()
    AppHelper.runEventLoop()
