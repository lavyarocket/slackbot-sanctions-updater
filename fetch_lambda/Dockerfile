FROM public.ecr.aws/lambda/python:3.11

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN yum install -y gcc gcc-c++ make
RUN pip install -r requirements.txt

# Set the CMD to your handler (filename.function)
CMD ["handler.handler"]