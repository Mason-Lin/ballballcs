@echo off
pushd "%~dp0.."
echo "Linter"
docker build --pull --target=dev-linter --network=host -t docker_name:dev-linter .
if not %errorlevel% == 0 goto FAIL


echo "Utest Coverage"
docker build --pull --target=dev-coverage --network=host -t docker_name:dev-coverage .
set errorcode=%errorlevel%
docker create --name=container_name docker_name:dev-coverage
docker cp container_name:/app/junit.xml .
docker cp container_name:/app/coverage.xml .
docker cp container_name:/app/htmlcov .
docker rm -v container_name
if not %errorcode% == 0 goto FAIL


echo "Security"
docker build --pull --target=dev-security --network=host -t docker_name:dev-security .
if not %errorlevel% == 0 goto FAIL


echo "Build Prod Image"
docker build --network=host -t prod_docker .
if not %errorlevel% == 0 goto FAIL
echo Test Pass

goto END
:FAIL
echo Test Fail
pause

:END
