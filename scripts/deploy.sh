#!/bin/bash
# ONE-CLICK PRODUCTION DEPLOYMENT
docker-compose -f docker/docker-compose.prod.yml down
docker-compose -f docker/docker-compose.prod.yml up -d --build
docker logs -f institutional-perps-arb-bot
