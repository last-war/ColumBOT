#!/bin/bash

# Запустіть додаток за допомогою uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload