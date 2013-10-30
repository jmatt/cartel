#!/usr/bin/env bash

source=dist/Cartel.app
title=Cartel
size=16000
applicationName=${title}
backgroundPictureName=cartel_background.jpg
finalDMGName="Cartel.dmg"

hdiutil create -srcfolder "${source}" -volname "${title}" -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${size}k pack.temp.dmg

hdiutil detach -force /Volumes/"${title}"

device=$(hdiutil attach -readwrite -noverify -noautoopen "pack.temp.dmg" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')

mkdir /Volumes/"${title}"/.background
cp ${backgroundPictureName} /Volumes/"${title}"/.background
echo ${backgroundPictureName} /Volumes/"${title}"/.background

echo '
   tell application "Finder"
     tell disk "'${title}'"
           open
           set current view of container window to icon view
           set toolbar visible of container window to false
           set statusbar visible of container window to false
           set the bounds of container window to {400, 100, 654, 420}
           set theViewOptions to the icon view options of container window
           set arrangement of theViewOptions to not arranged
           set icon size of theViewOptions to 72
           set background picture of theViewOptions to file ".background:'${backgroundPictureName}'"
           make new alias file at container window to POSIX file "/Applications" with properties {name:"Applications"}
           set position of item "'${applicationName}'" of container window to {163, 100}
           set position of item "Applications" of container window to {163, 200}
           update without registering applications
           delay 5
           eject
     end tell
   end tell
' | osascript

chmod -R -f go-w /Volumes/"${title}"
sync
sync
hdiutil detach -force ${device}

if [ -e "${finalDMGName}" ]; then
    rm "${finalDMGName}"
fi

hdiutil convert "./pack.temp.dmg" -format UDZO -imagekey zlib-level=9 -o "${finalDMGName}"
rm -f ./pack.temp.dmg
