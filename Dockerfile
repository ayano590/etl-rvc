# Use CUDA base image
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

# Set working directory
WORKDIR /etl-rvc

# Set noninteractive mode and configure locale
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

# Install dependencies and configure Python 3.9
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        locales \
        ffmpeg \
        software-properties-common \
        build-essential \
        curl \
        python3.9 \
        python3.9-distutils \
        python3.9-dev && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen && update-locale LANG=en_US.UTF-8 && \
    add-apt-repository ppa:deadsnakes/ppa && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9 && \
    python3.9 -m pip install --no-cache-dir --upgrade pip==24.0 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements-docker.txt /etl-rvc/

# Install Python dependencies
RUN python -m pip install --no-cache-dir -r requirements-docker.txt

# Optional: Build and install portaudio if needed
# Uncomment if pyaudio is used
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends libasound2-dev && \
#     curl -O https://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz && \
#     tar -xvzf pa_stable_v190700_20210406.tgz && \
#     cd portaudio && ./configure && make && make install && cd .. && \
#     rm -rf portaudio pa_stable_v190700_20210406.tgz && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose the necessary port
EXPOSE 7865

# Define default command
CMD ["python", "infer_web.py"]