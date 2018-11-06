#!/bin/bash
# https://github.com/argaen/aiocache/blob/master/scripts/make_release

version=$(grep -o -E "([0-9]+\.[0-9]+\.[0-9]+)" async_sender/_version.py)
echo -n "New version number (current is $version): "
read new_version

echo -n "Are you sure? (y/n) "
read answer

if echo "$answer" | grep -iq "^y" ;then
  echo "Generating new release..."
  sed -i "s/$version/$new_version/" async_sender/_version.py
  git commit -a -m "Bump version $new_version"
  git tag -a "$new_version" -m "$new_version"
  git push --follow-tags

else
  exit 1
fi
