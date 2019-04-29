#!/bin/bash


main() {
    set -e
    local projectRoot=`pwd`/../backend

    # Acquire the server version
    local version=`PYTHONPATH=${projectRoot}:${PYTHONPATH} python3 -c "import brewer; print(brewer.__version__)"`

    local name="pybrewer_${version}"
    local packageName=${name}.deb
    local rootDir=${name}
    local installRoot=${rootDir}/usr/local/bin/pybrewer

    # Create a binary
    pyinstaller \
        -F \
        --hidden-import=ssc \
        ${projectRoot}/brewer/App.py

    # Cleanup
    rm -fv ${packageName}
    rm -rfv ${rootDir}

    mkdir -p ${rootDir}
    mkdir -p ${installRoot}


    # Install main files
    cp -rv \
        ${projectRoot}/brewer/app \
        ${projectRoot}/pybrewer_runner.sh \
        ${installRoot}/

    cp -v \
        `pwd`/dist/App \
        ${installRoot}/pybrewer

    # Create the manifest
    mkdir -p ${rootDir}/DEBIAN

    # Generate control file
    echo "Package: pybrewer" >> ${rootDir}/DEBIAN/control
    echo "Version: ${version}" >> ${rootDir}/DEBIAN/control
    echo "Section: base" >> ${rootDir}/DEBIAN/control
    echo "Priority: optional" >> ${rootDir}/DEBIAN/control
    echo "Architecture: armhf" >> ${rootDir}/DEBIAN/control
    echo "Maintainer: Nikola Spiric <nikola.spiric.ns@gmail.com>" >> ${rootDir}/DEBIAN/control
    echo "Description: PyBrewer" >> ${rootDir}/DEBIAN/control

    # Create the package
    dpkg-deb --build ${rootDir}

    echo "###################"
    echo "created: `pwd`/${packageName}"

    return $?
}

main "$@"