until docker exec -it analytics pg_isready 2>/dev/null;  do
    echo "Waiting..."
    sleep 0.5
done
docker exec -it analytics createdb dev
pipenv run python tests/test.py
