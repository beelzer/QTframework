# Multi-stage Dockerfile for QT Framework
# Supports both development and production builds

# ============================================================================
# Stage 1: Base Python image with system dependencies
# ============================================================================
FROM python:3.14-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=true \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for QT
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    # QT dependencies
    libglib2.0-0 \
    libgl1-mesa-glx \
    libxcb1 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libfontconfig1 \
    libdbus-1-3 \
    # X11 for headless testing
    xvfb \
    x11-utils \
    # Additional tools
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Stage 2: Builder stage with UV
# ============================================================================
FROM base AS builder

# Install UV for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /build

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using UV
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache .

# Copy source code
COPY src/ src/
COPY README.md LICENSE ./

# Build the package
RUN . /opt/venv/bin/activate && \
    uv pip install --no-cache -e .

# ============================================================================
# Stage 3: Development image
# ============================================================================
FROM base AS development

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --from=builder /build /app

# Install development dependencies
COPY pyproject.toml uv.lock* ./
RUN pip install -e .[dev,docs]

# Install additional dev tools
RUN pip install \
    ipython \
    ipdb \
    jupyter \
    notebook

# Create non-root user for development
RUN useradd -m -s /bash developer && \
    chown -R developer:developer /app
USER developer

# Set QT environment for headless operation
ENV QT_QPA_PLATFORM=offscreen \
    QT_DEBUG_PLUGINS=1

# Expose ports for development servers
EXPOSE 8000 8888 6006

# Volume for code mounting in development
VOLUME ["/app"]

# Default command for development
CMD ["python", "-m", "IPython"]

# ============================================================================
# Stage 4: Test runner image
# ============================================================================
FROM base AS test-runner

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application and test code
COPY --from=builder /build /app
COPY tests/ tests/
COPY pytest.ini .coveragerc* ./

# Install test dependencies
RUN pip install pytest pytest-qt pytest-cov pytest-xdist

# Setup Xvfb for GUI testing
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1920x1080x24 &\nexport DISPLAY=:99\nexec "$@"' > /usr/local/bin/xvfb-run.sh && \
    chmod +x /usr/local/bin/xvfb-run.sh

# Run tests by default
ENTRYPOINT ["/usr/local/bin/xvfb-run.sh"]
CMD ["pytest", "tests/", "--cov=src/qtframework", "--cov-report=term-missing"]

# ============================================================================
# Stage 5: Production image
# ============================================================================
FROM base AS production

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -s /bin/bash qtuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --from=builder /build /app

# Set ownership
RUN chown -R qtuser:qtuser /app

# Switch to non-root user
USER qtuser

# Set production environment variables
ENV PYTHONOPTIMIZE=1 \
    QT_QPA_PLATFORM=xcb

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import qtframework; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "qtframework"]

# ============================================================================
# Stage 6: Documentation builder
# ============================================================================
FROM base AS docs-builder

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application and docs
COPY --from=builder /build /app
COPY docs/ docs/

# Install documentation dependencies
RUN pip install sphinx furo sphinx-autodoc-typehints myst-parser

# Build documentation
RUN sphinx-build -b html docs docs/_build/html

# ============================================================================
# Stage 7: Minimal runtime for CI/CD
# ============================================================================
FROM python:3.14-alpine AS minimal

# Install minimal QT runtime dependencies
RUN apk add --no-cache \
    libstdc++ \
    libgcc \
    glib \
    libx11 \
    libxcb \
    libxkbcommon \
    fontconfig \
    dbus

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
WORKDIR /app
COPY --from=builder /build/src /app/src

# Create non-root user
RUN adduser -D -s /bin/sh qtuser && \
    chown -R qtuser:qtuser /app
USER qtuser

# Set minimal environment
ENV QT_QPA_PLATFORM=minimal \
    PYTHONOPTIMIZE=2

# Run
CMD ["python", "-m", "qtframework"]

# ============================================================================
# Default target is production
# ============================================================================
FROM production
