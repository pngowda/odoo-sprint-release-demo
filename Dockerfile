FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    openssh-client \
    shellcheck \
    shfmt \
    gcc \
    build-essential \
    && pip install --upgrade pip \
    && pip install flake8 black bandit coverage \
    && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Odoo dependencies as needed
RUN pip install -r requirements.txt
# Make sure odoo-bin is available in PATH or copied
CMD ["/bin/bash"]