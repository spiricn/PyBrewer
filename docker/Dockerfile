FROM resin/rpi-raspbian

RUN apt update

# Install dependencies
RUN apt install \
    build-essential \
    python3 \
    python3-setuptools \
    python3-pip \
    libpython3.4-dev \
    zlib1g-dev \
    git

RUN pip3 install pyinstaller

RUN pip3 install dropbox

# Install SSC
RUN git clone https://github.com/spiricn/ssc.git
RUN cd ssc && python3 setup.py install

# Install PyRPi
RUN git clone https://github.com/spiricn/PyRPi.git
RUN cd PyRPi && python3 setup.py install

# Build PyBrewer
RUN git clone https://github.com/spiricn/PyBrewer.git
RUN cd PyBrewer/package && ./package.sh
