#!/bin/sh

create-dmg/create-dmg \
    --volname "florrioafk" \
    --background "florrioafk.png" \
    --window-pos 200 120 \
    --window-size 500 320 \
    --icon-size 80 \
    --icon "App.app" 125 175 \
    --hide-extension "App.app" \
    --app-drop-link 375 175 \
    "App.dmg" \
    "App.app"