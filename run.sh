#!/usr/bin/env bash

echo "starting backend..."
cd api || exit 1
python src/app.py &

echo "starting frontend..."
cd ../web || exit 1
npm run dev &

wait
