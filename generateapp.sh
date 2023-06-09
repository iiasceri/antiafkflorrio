rm -rf build;rm -rf dist;rm -rf florrioafk.spec
/opt/homebrew/opt/python@3.9/bin/python3.9 -m PyInstaller --name 'afkinflorrio' --icon 'icon.icns' --windowed florrioafk.py
#create-dmg \
#  --volname "afkinflorrio" \
#  --volicon "icon.icns" \
#  --window-pos 200 120 \
#  --window-size 600 300 \
#  --icon-size 512 \
#  --icon "afkinflorrio.app" 175 120 \
#  --hide-extension "afkinflorrio.app" \
#  --app-drop-link 425 120 \
#  "dist/afkinflorrio.dmg" \
#  "dist/dmg/"
#brew install codesign
#codesign -fs my-new-cert --force --deep --timestamp --options runtime whattosign