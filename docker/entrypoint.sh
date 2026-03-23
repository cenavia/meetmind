#!/bin/sh
# Ajusta hilos CPU para PyTorch/OpenMP en el contenedor (mejor uso de varios cores).
set -e
if [ -z "${OMP_NUM_THREADS:-}" ]; then
  OMP_NUM_THREADS="$(nproc 2>/dev/null || echo 4)"
  export OMP_NUM_THREADS
fi
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-$OMP_NUM_THREADS}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-$OMP_NUM_THREADS}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-$OMP_NUM_THREADS}"

exec "$@"
