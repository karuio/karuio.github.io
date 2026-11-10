#!/usr/bin/env bash
# Publish a committed, built static tree to the existing X News Nginx vhost.
# Bootstrap TLS/vhost once using deploy/xnews.nginx.conf; see DEPLOYMENT.md.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "$(git status --porcelain)" ]]; then
  echo 'Commit the tested build before deployment.' >&2
  exit 1
fi
XNEWS_RELEASE=$(git rev-parse --short=12 HEAD)
XNEWS_REMOTE=/opt/qiaomu-apps/xnews
ssh -o BatchMode=yes qiaomu-hostinger "test -f /etc/letsencrypt/live/xnews.qiaomu.ai/fullchain.pem && mkdir -p '$XNEWS_REMOTE/releases/$XNEWS_RELEASE'"
rsync -az public/ "qiaomu-hostinger:$XNEWS_REMOTE/releases/$XNEWS_RELEASE/"
ssh -o BatchMode=yes qiaomu-hostinger bash -s -- "$XNEWS_RELEASE" <<'REMOTE'
set -euo pipefail
XNEWS_RELEASE=$1
cd /opt/qiaomu-apps/xnews
test -f "releases/$XNEWS_RELEASE/index.html"
nginx -t
if [[ -L current ]]; then
  ln -sfn "$(readlink current)" previous
fi
ln -sfn "releases/$XNEWS_RELEASE" current.next
mv -Tf current.next current
printf 'set $xnews_release "%s";\n' "$XNEWS_RELEASE" > release.nginx.conf
nginx -t
nginx -s reload
printf 'Published X News release %s\n' "$XNEWS_RELEASE"
REMOTE
