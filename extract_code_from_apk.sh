
## Start analyzing the apk files
java -jar apktool1.5.2/apktool.jar d -f input/com.metago.astro.apk output/

## Create the dex file
jar xvf input/com.metago.astro.apk classes.dex
mv classes.dex output

dex2jar-0.0.9.15/dex2jar.sh output/classes.dex

## Switching locations was the only way to have everything output in the appropriate location.
cd output
jar xvf classes_dex2jar.jar 
cd ..

### An ugly hack
cd ../../

## Now convert all of the .class files to .java
java -jar jd-cmd/jd-cli/target/jd-cli.jar output/ -od output/
