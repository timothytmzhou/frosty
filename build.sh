# builds all the docker containers in languages/
for dockerfile in languages/*.dockerfile
do
  docker build $dockerfile -t ohm/$dockerfile
done