#!/bin/bash

# PG IP Whitelister v1.1.0 - Docker Build and Push Script
# This script builds and pushes the Docker image with proper version tags

set -e

VERSION="1.1.0"
IMAGE_NAME="pmylward/pg-ip-whitelister"

echo "🏗️  Building PG IP Whitelister v${VERSION}..."

# Build the Docker image
echo "Building Docker image: ${IMAGE_NAME}:v${VERSION}"
docker build -t "${IMAGE_NAME}:v${VERSION}" .

# Tag as latest
echo "Tagging as latest: ${IMAGE_NAME}:latest"
docker tag "${IMAGE_NAME}:v${VERSION}" "${IMAGE_NAME}:latest"

# Display built images
echo "✅ Built images:"
docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
echo "🚀 Ready to push to Docker Hub!"
echo ""
echo "To push the images, run:"
echo "  docker push ${IMAGE_NAME}:v${VERSION}"
echo "  docker push ${IMAGE_NAME}:latest"
echo ""
echo "Or run both with:"
echo "  docker push ${IMAGE_NAME}:v${VERSION} && docker push ${IMAGE_NAME}:latest"
echo ""

# Optional: Test the image locally
echo "🧪 To test the image locally:"
echo "  docker run -d -p 5000:5000 \\"
echo "    -e PANGOLIN_API_URL=http://your-pangolin:3003/v1 \\"
echo "    -e PANGOLIN_API_KEY=your-api-key \\"
echo "    -e PANGOLIN_ORG_ID=your-org-id \\"
echo "    -e SECRET_KEY=\$(openssl rand -hex 32) \\"
echo "    ${IMAGE_NAME}:v${VERSION}"
