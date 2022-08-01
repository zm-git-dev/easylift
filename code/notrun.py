### not run
### this script is for me to check something

### add soft link
rm -rf liftover; ln -s ../db/liftover ./liftover # link to in-house db
rm -rf liftover; mkdir liftover; touch liftover/test # make empty fold


### check module version
from importlib_metadata import version
print(version('numpy'))
print(version('argparse '))