
```bash
docker build --tag layerexample .

docker inspect layerexample | jq .[].GraphDriver

for low_layer in $(docker inspect layerexample | jq  -r .[].GraphDriver.Data.LowerDir | tr ":" " ")
do
    echo "Layer path : ${low_layer}"
    echo "Layer content in /var/tmp : "
    sudo ls ${low_layer}/var/tmp
done


docker run --rm -it  -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive layerexample


# docker save layerexample -o layereaxmple.tar
# tar -vf layereaxmple.tar

# tar -xvf layereaxmple.tar <PATH_FILE_SHA256>
# cat <PATH_FILE_SHA256> may look like

# vm00@vm00:~/tp-cs-containers-student/docker$ tar -xvf image.tar blobs/sha256/b0d2b18cc89e0892f3963752c5a3c7db356bcb2ffd9526bd45ee71d261247a7e
# blobs/sha256/b0d2b18cc89e0892f3963752c5a3c7db356bcb2ffd9526bd45ee71d261247a7e
# vm00@vm00:~/tp-cs-containers-student/docker$ cat blobs/sha256/b0d2b18cc89e0892f3963752c5a3c7db356bcb2ffd9526bd45ee71d261247a7e
# var/0000755000000000000000000000000014745565345010056 5ustar0000000000000000var/tmp/0001777000000000000000000000000014764255771010663 5ustar0000000000000000var/tmp/.wh.fileTODELETE0000600000000000000000000000000014764255771013317 0ustar0000000000000000vm00@vm00:~/tp-cs-containers-student/docker$


```