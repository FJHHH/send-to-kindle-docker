# 使用官方的Python基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到容器的工作目录中
COPY . /app

# 安装依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 复制你的Python脚本到容器中
COPY monitor.py .

# 将/data挂载为数据卷，以便在容器外可以添加或删除文件
VOLUME ["/data"]

# 设置启动命令
CMD ["python", "monitor.py"]