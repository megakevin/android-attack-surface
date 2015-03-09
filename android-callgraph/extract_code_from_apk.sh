## Need to have these:
## openjdk-7-jdk
## apktool
## dex2jar


## Start analyzing the apk files
java -jar apktool1.5.2/apktool.jar d -f input/com.facebook.orca.apk output/

## Create the dex file
jar xvf input/com.zaneashby.ircshare.apk classes.dex
mv classes.dex output

## Create the jar based on the dex file
dex2jar-0.0.9.15/dex2jar.sh output/classes.dex

## Extract the contents of the jar
cd output
jar xvf classes_dex2jar.jar 
cd ..

## Now convert all of the .class files to .java
java -jar jd-cmd/jd-cli/target/jd-cli.jar output/ -od output/

## Obtain call graph from jar
java -jar java-callgraph/target/javacg-0.1-SNAPSHOT-static.jar output/classes_dex2jar.jar


