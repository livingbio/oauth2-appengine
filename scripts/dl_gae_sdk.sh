#!/bin/bash
APPENGINE_SDK_VERSION=1.9.17
APPENGINE_SDK_ZIPFILE=google_appengine_${APPENGINE_SDK_VERSION}.zip

echo "Downloading Google App Engine SDK..."
wget --quiet http://storage.googleapis.com/tagtoo_public/google-app-engine-sdk/${APPENGINE_SDK_ZIPFILE}

echo "Extracting Google App Engine SDK..."
unzip -q ${APPENGINE_SDK_ZIPFILE} > /dev/null

echo "Deleting archive files..."
rm -rf ${APPENGINE_SDK_ZIPFILE}
