#!/bin/sh
# Usage: sh deploy.sh <dev|staging|prod> [--no-pull] [--collectstatic]
#
# All env-specific values live in build_meta/.env_<env>, which doubles as
# the containers' env_file and as compose's --env-file.

ENV=$1
git_pull="true"
collectstatic="false"

PROJECT_HOME="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  echo "Usage: sh deploy.sh <dev|staging|prod> [options]"
  echo "  --help | prints usage info"
  echo "  --no-pull | Doesn't pull from git"
  echo "  --collectstatic | Runs collectstatic inside the container"
}

case $ENV in
  dev|staging|prod) ;;
  *) usage; exit 1 ;;
esac

for i in "$@"; do
  if [ "$i" = "--help" ]; then
    usage
    exit 0
  elif [ "$i" = "--no-pull" ]; then
    git_pull="false"
  elif [ "$i" = "--collectstatic" ]; then
    collectstatic="true"
  fi
done

ENV_FILE=$PROJECT_HOME/build_meta/.env_$ENV
COMPOSE="docker compose --env-file $ENV_FILE -p q-yaar-$ENV -f $PROJECT_HOME/docker/docker-compose.yml"

if [ "$git_pull" = "true" ] && [ "$ENV" != "dev" ]; then
  echo "Pulling from git"
  git -C $PROJECT_HOME/ pull
fi

$COMPOSE build
$COMPOSE up -d

if [ "$collectstatic" = "true" ]; then
  $COMPOSE exec q_yaar_core mkdir -p static
  $COMPOSE exec q_yaar_core python manage.py collectstatic --noinput
fi
