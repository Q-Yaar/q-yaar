run_db="false"
run_redisearch="false"

for i in $*; do
  if [ "$i" = "--help" ]; then
    echo "Usage: sh deploy-staging.sh [options]"
    echo "--help | prints usage info"
    echo "--run-db | Runs postgres db in container"
    echo "--run-redisearch | Starts redisearch in container"
    exit 0
  elif [ "$i" = "--run-db" ]; then
    run_db="true"
  elif [ "$i" = "--run-redisearch" ]; then
    run_redisearch="false"
  fi
done

docker compose -f docker-compose-dev.yml up --build -d q_yaar_core fast_worker slow_worker celery_beat

if [ "$run_db" = "true" ]; then
  docker compose -f docker-compose-dev.yml up -d db
fi

if [ "$run_redisearch" = "true" ]; then
  docker compose -f docker-compose-dev.yml up -d redisearch
fi
