# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 安装 Open3D 的依赖
RUN apt-get update && apt-get install -y libgomp1 && apt-get install -y libx11-dev && apt-get install -y libgl1-mesa-glx
RUN apt-get install -y cmake && apt-get install -y python3-dev && apt-get install -y build-essential
RUN apt-get install -y --fix-missing libjpeg-dev libpng-dev libtiff-dev libgtk-3-dev libflann-dev libomp-dev


# 设置工作目录
WORKDIR /app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 将依赖文件复制到容器中
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将项目文件复制到容器中
COPY . .

# 暴露7000端口
EXPOSE 6000

# 设置容器启动时执行的命令
CMD ["python", "web/app.py"]
