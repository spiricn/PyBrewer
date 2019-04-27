Raspberry PI based homebrew temperature controller

## Dependencies

* Python3

* SSC ( https://github.com/spiricn/ssc )
  Used as a HTTP server backend library.

* PyRPI ( https://github.com/spiricn/PyRPi )
  Hardware control utility library.

* PyInstaller ( http://www.pyinstaller.org/ )
  Used to package PyBrewer into a binary application.

### Buildling PyBrewer

To create a debian package run the packaging script:
```sh
cd package
./package.sh
```

This will create a pybrewer_x.x.x.deb package which you can install with:
```sh
sudo dpkg -i pybrewer_x.x.x.deb
```