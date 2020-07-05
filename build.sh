# builds all the docker containers in languages/
for dockerfile in languages/dockerfiles/*.dockerfile
do
  name=$(basename $dockerfile .dockerfile)
  docker build -f $dockerfile -t ohm/$name .
done