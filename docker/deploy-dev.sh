collectstatic="false"

PROJECT_HOME="$(cd "$(dirname "$0")/.." && pwd)"

for i in $*; do
  if [ "$i" = "--help" ]; then
    echo "Usage: sh deploy-dev.sh [options]"
    echo "--help | prints usage info"
    echo "--collectstatic | if collectstatic command needs to be run"
    exit 0
  elif [ "$i" = "--collectstatic" ]; then
    collectstatic="true"
  fi
done

echo "Setting variables"
. $PROJECT_HOME/q_yaar_platform/.env_docker

docker compose -f $PROJECT_HOME/docker/docker-compose-dev.yml build
docker compose -f $PROJECT_HOME/docker/docker-compose-dev.yml up -d

if [ "$collectstatic" = "true" ]; then
  docker compose -f $PROJECT_HOME/docker/docker-compose-dev.yml exec q_yaar_core mkdir -p static
  docker compose -f $PROJECT_HOME/docker/docker-compose-dev.yml exec q_yaar_core python manage.py collectstatic --noinput
fi
