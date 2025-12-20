git_pull="true"
collectstatic="false"

PROJECT_HOME="/home/game/q_yaar_backend/q-yaar"

for i in $*; do
  if [ "$i" = "--help" ]; then
    echo "Usage: sh deploy-staging.sh [options]"
    echo "--help | prints usage info"
    echo "--no-pull | Doesn't pull from git"
    echo "--collectstatic | if collectstatic command needs to be run"
    exit 0
  elif [ "$i" = "--no-pull" ]; then
    git_pull="false"
  elif [ "$i" = "--collectstatic" ]; then
    collectstatic="true"
  fi
done

echo "Setting variables"
. $PROJECT_HOME/build_meta/.env_staging

if [ "$git_pull" = "true" ]; then
  echo "Pulling from git"
  git -C $PROJECT_HOME/ pull
fi

sudo docker compose -f $PROJECT_HOME/docker/docker-compose-staging.yml build
sudo docker compose -f $PROJECT_HOME/docker/docker-compose-staging.yml up -d

if [ "$collectstatic" = "true" ]; then
  sudo docker compose -f $PROJECT_HOME/docker/docker-compose-staging.yml exec q_yaar_core mkdir static
  sudo docker compose -f $PROJECT_HOME/docker/docker-compose-staging.yml exec q_yaar_core python manage.py collectstatic --noinput
fi

if [ "$git_pull" = "true" ]; then
  sudo docker compose -f $PROJECT_HOME/docker/docker-compose-staging.yml exec q_yaar_core python manage.py migrate
fi