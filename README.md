# AuraAnim - engineering thesis
Engineering thesis project focused on designing and implementing a full-stack application for generating videos from text descriptions and other parameters from user. The project explores modern text-to-video approaches based on deep learning models and analyzes trade-offs between model quality and computational cost.

The system is built around a scalable backend using Python, FastAPI, and Ray, enabling parallel video generation and efficient model serving across a cluster. The system includes a Next.js-based web frontend that enables users to generate, preview, and manage videos. The backend integrates Stable Diffusion with AnimateDiff for text-to-video generation, using PostgreSQL for metadata persistence and MinIO for scalable object storage of generated media.

# CUDA WSL2 setup guide
In order to run CUDA-enabled containers the following dependencies are necessary:

- new NVIDIA drivers installed on **Windows**
- CUDA toolkit installed on WSL2 Ubuntu: https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0&target_type=deb_local
- NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/1.13.5/install-guide.html under section *Docker*

The dependencies should be installed in the order given above. To check if everything was installed correctly execute ```sudo docker run --rm --runtime=nvidia --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi```

Now, to build the image and run a container go to the backend directory and run ```docker build -t text-to-video-backend .```. To start a container from the image with GPU support run ```docker run --gpus all -p 8000:8000 -p 8265:8265 --shm-size=2.22gb text-to-video-backend```.

# Running using Docker Compose
To run the development version of the application together with supporting containers execute
```docker compose -f docker-compose.dev.yaml up --build``` from the ```docker``` directory.

# Database management

Adminer is included in the development Docker Compose setup for easy database inspection.

## Accessing Adminer

1. Make sure the development containers are running:
```bash
cd docker
docker compose -f docker-compose.dev.yaml up
```
2. Open your browser and navigate to: **http://localhost:8080**
3. Log in with the following credentials:
- **System:** `PostgreSQL`
- **Server:** `postgres-dev`
- **Username:** `dev_user`
- **Password:** `dev_password`
- **Database:** `text_to_video_dev`

# Object Storage Management

MinIO Console is included in the development Docker Compose setup for managing video storage.

## Accessing MinIO

1. Make sure the development containers are running:
```bash
cd docker
docker compose -f docker-compose.dev.yaml up
```
2. Open your browser and navigate to: **http://localhost:9001**
3. Log in with the following credentials:
- **Username:** `minio_admin`
- **Password:** `minio_pass123`
